"""External PC/Quest resolution settings. Device writes require the explicit push button."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'settings.json'
ADB = ROOT.parent / 'FGO-Quest/tools/android/sdk/platform-tools/adb.exe'
REMOTE = '/sdcard/Android/data/com.fgovr.quest/files/vrhost.txt'
PC = (100,110,125,150)
QUEST = (100,110,125)

def load():
    settings = json.loads(CONFIG.read_text(encoding='utf-8-sig')) if CONFIG.exists() else {}
    return {'schema':1, 'pc_scale':settings.get('pc_scale',100),
            'quest_scale':settings.get('quest_scale',100)}

def validate(settings):
    for key,values in [('pc_scale',PC),('quest_scale',QUEST)]:
        if type(settings[key]) is not int or settings[key] not in values:
            raise ValueError(f'Unsupported {key}: {settings[key]}')

def save(settings):
    validate(settings)
    CONFIG.write_text(json.dumps(settings,indent=2)+'\n',encoding='utf-8')
    (ROOT/'quest-vrhost.txt').write_text(
        '# FGO internal rendering; 100=OFF, restart the app after changing.\n'
        f'fgo_render_scale={settings["quest_scale"]}\n',encoding='utf-8')

def merge_quest(existing,scale):
    if scale not in QUEST: raise ValueError('Unsupported Quest scale')
    lines = [line for line in existing.splitlines()
             if not re.match(r'^\s*fgo_render_scale\s*=',line)]
    return '\n'.join(lines + [f'fgo_render_scale={scale}'])+'\n'

def push_quest(settings):
    validate(settings)
    if not ADB.is_file(): raise RuntimeError('Bundled ADB was not found.')
    def adb(*args,check=True):
        result = subprocess.run([str(ADB),*args],capture_output=True,text=True,
                                encoding='utf-8',errors='replace',timeout=30)
        if check and result.returncode: raise RuntimeError(result.stderr or result.stdout)
        return result
    devices = [line.split()[0] for line in adb('devices').stdout.splitlines()[1:]
               if len(line.split())>=2 and line.split()[1]=='device']
    if len(devices)!=1: raise RuntimeError('Connect one Quest by USB and allow USB debugging.')
    package = adb('-s',devices[0],'shell','dumpsys','package','com.fgovr.quest').stdout
    version = re.search(r'versionCode=(\d+)',package)
    if not version or int(version.group(1))<2:
        raise RuntimeError('Install FGO VR Quest 3 version 0.2.0 or later first.')
    has_file = adb('-s',devices[0],'shell','test','-f',REMOTE,check=False).returncode==0
    existing = adb('-s',devices[0],'shell','cat',REMOTE).stdout if has_file else ''
    evidence = ROOT/'evidence'/('quest_settings_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    evidence.mkdir(parents=True,exist_ok=False)
    (evidence/'previous_vrhost.txt').write_text(existing,encoding='utf-8')
    merged = evidence/'vrhost.txt'
    merged.write_text(merge_quest(existing,settings['quest_scale']),encoding='utf-8')
    adb('-s',devices[0],'shell','mkdir','-p',REMOTE.rsplit('/',1)[0])
    result = adb('-s',devices[0],'push',str(merged),REMOTE)
    (evidence/'push.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    return 'Quest settings pushed. Close and restart the game to apply them.'

def gui():
    import tkinter as tk
    from tkinter import ttk,messagebox
    window = tk.Tk()
    window.title('FGO VR Resolution Settings')
    window.geometry('590x305')
    window.resizable(False,False)
    panel = ttk.Frame(window,padding=18)
    panel.pack(fill='both',expand=True)
    initial = load()
    labels = {100:'OFF: original resolution',110:'1.10x (about 21% more pixels)',
              125:'1.25x (about 56% more pixels)',150:'1.50x (about 125% more pixels; PC only)'}
    pc = tk.StringVar(value=labels.get(initial['pc_scale'],labels[100]))
    quest = tk.StringVar(value=labels.get(initial['quest_scale'],labels[100]))
    for row,title,variable,values in [(0,'PC / VDXR',pc,PC),(1,'Quest 3 standalone',quest,QUEST)]:
        ttk.Label(panel,text=title).grid(row=row,column=0,padx=(0,12),pady=8,sticky='w')
        ttk.Combobox(panel,textvariable=variable,values=[labels[x] for x in values],
                     state='readonly',width=43).grid(row=row,column=1,sticky='w')
    ttk.Label(panel,text='Default: OFF. Higher resolution uses more GPU power and memory.\n'
                        'PC: save and restart. Quest: push settings over USB, then restart.\n'
                        'OFF restores original resolution. This tool does not start or stop games.',
              wraplength=545).grid(row=2,column=0,columnspan=2,pady=12,sticky='w')
    status = tk.StringVar(value='Settings unchanged.')
    def selected():
        inverse = {v:k for k,v in labels.items()}
        return {'schema':1,'pc_scale':inverse[pc.get()],'quest_scale':inverse[quest.get()]}
    def store():
        try:
            save(selected())
            status.set('Saved. Connect by USB to push the Quest settings.')
        except Exception as error: messagebox.showerror('Save failed',str(error))
    def push():
        try:
            save(selected())
            status.set(push_quest(selected()))
        except Exception as error: messagebox.showerror('Push failed',str(error))
    buttons = ttk.Frame(panel)
    buttons.grid(row=3,column=0,columnspan=2,sticky='w')
    ttk.Button(buttons,text='Save settings',command=store).pack(side='left',padx=(0,12))
    ttk.Button(buttons,text='Push Quest settings (USB)',command=push).pack(side='left')
    ttk.Label(panel,textvariable=status,wraplength=545).grid(row=4,column=0,columnspan=2,pady=14,sticky='w')
    window.mainloop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pc',type=int,choices=PC)
    parser.add_argument('--quest',type=int,choices=QUEST)
    parser.add_argument('--push-quest',action='store_true')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    if args.pc is None and args.quest is None and not args.push_quest and not args.check:
        gui(); return
    settings = load()
    if args.pc is not None: settings['pc_scale']=args.pc
    if args.quest is not None: settings['quest_scale']=args.quest
    validate(settings)
    if args.pc is not None or args.quest is not None: save(settings)
    if args.push_quest: print(push_quest(settings))
    print(json.dumps(settings))

if __name__=='__main__': main()
