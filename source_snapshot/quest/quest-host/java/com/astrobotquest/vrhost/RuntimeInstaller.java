// SPDX-License-Identifier: GPL-2.0-or-later
package com.fgovr.quest;

import android.content.Context;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Unpacks the Linux runtime the emulator runs in (its libraries, the GPU driver, the emulator
 * core itself) from the app's assets into the app's files folder. The assets carry a stamp of
 * what they hold; a folder with the same stamp is left alone.
 */
final class RuntimeInstaller {
    private RuntimeInstaller() {}

    /** Returns true when the runtime had to be unpacked, false when it was there already. */
    static boolean install(Context context, File runtime) throws IOException {
        String stamp;
        try (InputStream in = context.getAssets().open("runtime.stamp")) {
            stamp = new String(readAll(in), StandardCharsets.UTF_8).trim();
        }
        File stampFile = new File(runtime, ".stamp");
        if (stampFile.isFile()
                && new String(Files.readAllBytes(stampFile.toPath()), StandardCharsets.UTF_8)
                        .trim().equals(stamp)) {
            return false;
        }

        deleteRecursively(runtime);
        runtime.mkdirs();
        String root = runtime.getCanonicalPath() + File.separator;
        byte[] buffer = new byte[1 << 16];
        try (ZipInputStream zip = new ZipInputStream(context.getAssets().open("runtime.zip"))) {
            for (ZipEntry entry = zip.getNextEntry(); entry != null; entry = zip.getNextEntry()) {
                File target = new File(runtime, entry.getName());
                if (!target.getCanonicalPath().startsWith(root)) {
                    throw new IOException("bad runtime entry " + entry.getName());
                }
                if (entry.isDirectory()) {
                    target.mkdirs();
                    continue;
                }
                target.getParentFile().mkdirs();
                try (FileOutputStream out = new FileOutputStream(target)) {
                    for (int count = zip.read(buffer); count > 0; count = zip.read(buffer)) {
                        out.write(buffer, 0, count);
                    }
                }
                target.setExecutable(true, true);
            }
        }
        Files.write(stampFile.toPath(), stamp.getBytes(StandardCharsets.UTF_8));
        return true;
    }

    private static byte[] readAll(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        for (int count = in.read(buffer); count > 0; count = in.read(buffer)) {
            out.write(buffer, 0, count);
        }
        return out.toByteArray();
    }

    static void deleteRecursively(File file) {
        File[] children = file.listFiles();
        if (children != null) {
            for (File child : children) {
                deleteRecursively(child);
            }
        }
        file.delete();
    }
}
