# FGO VR — PCVR 0.2.1 / Quest 3 0.2.0

[English](README.md) | [日本語](README.ja.md) | [简体中文](README.zh-CN.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Português](README.pt.md) | [Italiano](README.it.md)

AstroQuest/shadPS4 ベースの互換ビルドで、**Fate/Grand Order VR feat. Mash Kyrielight**をプレイできます。本プロジェクトの対象は日本版PS4タイトル **CUSA09078**、ゲームバージョン **01.00 / 01.01** です。

- **PCVR:** Virtual Desktop と VDXR を使用する OpenXR。
- **Quest 3単体動作:** FEX と Turnip を使うローカルARM64コア。PCからゲーム映像をストリーミングしません。

本プロジェクトとダウンロードを公開しました。[紹介動画を見る](https://saberwatchmanga.github.io/FGO-VR/?lang=ja)。パッケージにPS4ゲームデータ、PKG、ファームウェア、鍵、セーブデータは含まれません。ご自身で抽出したゲームをご用意ください。

## 紹介動画

[![FGO VR — 紹介動画を再生](docs/video-thumbnail.png)](https://saberwatchmanga.github.io/FGO-VR/?lang=ja)

**[▶ 紹介動画を再生](https://saberwatchmanga.github.io/FGO-VR/?lang=ja)** · [YouTubeで見る](https://youtu.be/zBSpUSqpUaw)

## ダウンロード

Windowsポータブル版の完全なフォルダー、Quest APK、ソースは[リリースv0.2.1](https://github.com/saberwatchmanga/FGO-VR/releases/tag/v0.2.1)からダウンロードできます。

| ファイル | 内容 |
| --- | --- |
| [FGO-VR-0.2.1-PCVR-Windows.zip](https://github.com/saberwatchmanga/FGO-VR/releases/download/v0.2.1/FGO-VR-0.2.1-PCVR-Windows.zip) | Windows PCVRビルドと外部解像度設定ツール |
| [FGO-VR-0.2.0-Quest3.apk](https://github.com/saberwatchmanga/FGO-VR/releases/download/v0.2.1/FGO-VR-0.2.0-Quest3.apk) | Quest 3単体動作用ビルド。このPC更新では変更なし |
| [FGO-VR-0.2.1-Source.zip](https://github.com/saberwatchmanga/FGO-VR/releases/download/v0.2.1/FGO-VR-0.2.1-Source.zip) | 固定済みパッチ、変更したソーススナップショット、ビルド参照資料、ライセンス |
| `SHA256SUMS` / `artifact-manifest.json` | ファイル検証情報と各コンポーネントのバージョン |

## Windows / PCVR クイックスタート

必要なもの：64ビット版Windows、Vulkan対応GPUとドライバー、Microsoft Visual C++ランタイム、PC上のVirtual Desktop Streamer、ヘッドセット上のVirtual Desktop。

1. `FGO-VR-0.2.1-PCVR-Windows.zip`を展開します。
2. `eboot.bin`を含む抽出済みベースゲームを`FGO-PC/games/CUSA09078`に置きます。任意のアップデートは隣の`FGO-PC/games/CUSA09078-UPDATE`に置きます。ベースゲームなしではアップデートを実行できません。
3. Virtual Desktopでヘッドセットを接続し、Streamerを起動したままにします。
4. **`Launch-PCVR.cmd`**をダブルクリックします。このランチャーはシステム全体のOpenXR設定を変更せず、このプロセスでVDXRを選択します。終了するにはゲームウィンドウを閉じます。
5. 解像度を変更するには**`Resolution-Settings.cmd`**を開きます。Python 3とTkが必要です。設定を保存してゲームを再起動してください。Pythonがない場合は`FGO-Resolution/settings.json`を編集するか、`profiles`内の直接起動ランチャーを使います。
6. **`Launch-PCVR-Original.cmd`**は常に元の解像度のビルドを、同じセーブデータで起動します。

中国語名の元のランチャーも引き続き収録されています。任意のシステムフォントはAstroQuest upstreamの手順に従ってください。ゲーム機のシステムファイルは同梱されません。

セーブ先：`FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`。タイトルのフォルダー全体をバックアップする前にゲームを終了してください。

## Quest 3単体動作のクイックスタート

`FGO-VR-0.2.0-Quest3.apk`をインストールします（パッケージ`com.fgovr.quest`、バージョンコード2）。同じ署名で更新すればアプリデータを維持できる場合があります。USBデバッグを有効にし、抽出したゲームフォルダーを次の場所へコピーします。

```text
/data/local/tmp/fgovr/games/CUSA09078
/data/local/tmp/fgovr/games/CUSA09078-UPDATE
```

2番目のパスは任意の1.01更新用です。更新を持っている場合のみコピーしてください。

ファイルを読み取り可能にしてください。コマンドと更新方法は[Questのインストール手順](docs/INSTALL_QUEST.md)を参照してください。

Questを1台だけUSB接続した状態で、Windows設定ツールからQuestへ解像度設定を送信し、アプリを終了して再起動します。このツールは既存設定をバックアップし、`fgo_render_scale`だけを変更します。

ログと設定は`/sdcard/Android/data/com.fgovr.quest/files/`にあります。`vrhost.txt`では`fgo_render_scale=100/110/125`を指定できます。起動後、ゲームはヘッドセット上でローカル実行されます。

## 解像度プロファイル

どちらのコンポーネントも既定値は**100 / OFF**です。これは100% / 1.00xに相当し、元の解像度を維持します。値を上げるとGPUとメモリーの使用量が増えます。これはゲーム内部の描画プロファイルで、VDXRに表示される解像度の割合とは別の指標です。

| プロファイル | PCVR | Quest 3 | 確認された結果 |
| --- | --- | --- | --- |
| 100 | 元の解像度 | 元の解像度 | Questではエイリアシングが強いとの報告 |
| 110 | 利用可能 | 利用可能 | Questでは許容範囲だがエイリアシングが見えるとの報告 |
| 125 | 起動のみ確認 | 利用可能 | Questでは目立つカクつきがあるとの報告 |
| 150 | 利用可能 | PCのみ | PCVR/VDXRで画質が良く、全編クリアしたとのユーザー報告 |

Questでは**110**を最初の推奨プロファイルとします。紹介動画のQuest映像は単体動作の100 (1.00x)で収録されており、PCよりエイリアシングが目立ちます。ゲーミングPCがある場合は、Virtual Desktop経由のPCVRストリーミングを推奨します。性能が低い場合は100に戻してください。テストしたPCはi5-13400F / RTX 4070 / 64 GB RAMです。定量的なFPS値や全編を通した性能は主張していません。

検証済みの片目あたりの描画ターゲットは、100で1408×1512、110で1536×1663、125で1792×1890、PC150で2048×2268です。このパッチはゲーム本来の正規リクエスト1.4fを置き換え、他のリクエストとアロケーションチェックを維持し、スケールが繰り返し乗算されるのを防ぎます。

### PCVR 0.2.1の遷移時クラッシュ修正

高解像度では、以前ストーリー中の遷移でゲームの固定グラフィックスメモリープールが枯渇していました。その後、不正なメモリー不足メッセージが原因で二度目のクラッシュが発生していました。PCVR 0.2.1ではグラフィックスプールと、それに対応するプロセス内Backing/Directメモリー予算を同時に拡張し、メッセージ形式も修正しています。追加予算は保存設定には書き込まれません。

**2026年10月7日**、ユーザーは**PCVR / VDXR 1.50xでゲーム全編をクリアした**ことを確認しました。以前クラッシュしていた遷移も再テストに合格し、記録されたセッションは正常に終了しました。PC125/150の起動確認と100へのロールバック確認も合格しています。Quest APKとQuestソースは0.2.0のままで、このPC修正はQuestには適用されていません。

受け入れ済みコアのSHA-256は `563be6008f73855c3b4425c93bca104692999e97f0fb16cf956c5d3aa40123c1` です。

[テスト詳細](TESTING.md)と[ユーザー受け入れ記録](docs/USER_ACCEPTANCE_20261007.md)を参照してください。

- 別の後日のPC150セッションではUnityのプリロード中にアクセス違反で終了しました。原因は未特定です。[テスト詳細](TESTING.md)を参照してください。

## 操作

| 入力 | 割り当て |
| --- | --- |
| Left Touch stick | メニュー操作 |
| Left / right grip | L1 / R1 |
| Left / right trigger | L2 / R2 |
| Right A | Cross / 決定 |
| 左右のスティックを同時に押す | リセンター |
| Keyboard Q / E | 決定 |
| Keyboard arrows | メニュー選択 |

右手のエイム姿勢は、ゲーム標準のDualShockトラッキングに接続されます。基本操作は動作します。Moveの完全な動作、正確なポインティング、すべてのトレーニング操作は検証されていません。

## 現在の制限

- ユーザーのヘッドセットではQuest125にカクつきがあり、Quest110にもエイリアシングが残っています。
- **PCVR / VDXR 1.50x：ユーザーが全編クリアを確認済みです。** 今回の修正でPC125について確認したのは起動までです。
- 繰り返し実行時の安定性、ヘッドセットで測定したFPS、他のハードウェアでの快適性は個別に評価していません。
- 追加のリプロジェクションレイヤー、Moveの完全対応、一部トラッキングインターフェースには未対応部分があります。
- このビルドの対象はFGO VRです。他のPSVRゲームには個別の互換性確認が必要です。

## ソース、ビルド、クレジット

[AstroQuest](https://github.com/bigmak94/AstroQuest)と[shadPS4](https://github.com/shadps4-emu/shadPS4)をベースにしています。AstroQuestはコミット`9f42c44d4e838e3a0df67913e350c4f098110862`に固定しています。

プラットフォーム別の完全なパッチは`patches`、変更したファイルは`source_snapshot`にあります。**選択したプラットフォーム用の完全なパッチを1つ適用してください。前段階のパッチを重ねて適用しないでください。**

`tools/prepare_source.py`は固定されたupstreamソースを取得し、選択したプラットフォームパッチを適用します。固定入力と参照スクリプトは[ビルド手順](docs/BUILD.md)を参照してください。一部の開発者パスは調整が必要です。クリーンな環境でワンクリックビルドできるとはしていません。リリース署名鍵は含まれません。

ソースに関する告知はGPL-2.0-or-laterおよび該当するサードパーティライセンスに従って保持されています。[LICENSE](LICENSE)、[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)、upstreamの告知を参照してください。これは非公式の互換プロジェクトです。原作ゲームとキャラクターの権利は各権利者に帰属します。

## 支援

このプロジェクトが役に立ったら、[Ko-fi / terry2418](https://ko-fi.com/terry2418)で継続開発を支援できます。ご支援ありがとうございます。
