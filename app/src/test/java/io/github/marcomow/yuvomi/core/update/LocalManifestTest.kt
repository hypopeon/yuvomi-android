package io.github.marcomow.yuvomi.core.update

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class LocalManifestTest {
    private fun release(url: String, digest: String?) = Releases.Release(
        tag = "v0.2.0", assets = listOf(Releases.Asset("yuvomi-android-0.2.0.apk", url, 10, digest)),
    )
    @Test fun `home manifest accepts same origin https and sha256`() {
        val u = Releases.localNewest(listOf(release("https://home.lan/updates/app.apk", "sha256:" + "a".repeat(64))), "0.1.0", "https://home.lan")
        assertEquals("0.2.0", u?.version)
    }
    @Test fun `home manifest rejects foreign origin insecure url and missing checksum`() {
        for (url in listOf("https://elsewhere.lan/a.apk", "http://home.lan/a.apk", "https://home.lan:8443/a.apk")) {
            assertNull(Releases.localNewest(listOf(release(url, "sha256:" + "a".repeat(64))), "0.1.0", "https://home.lan"))
        }
        assertNull(Releases.localNewest(listOf(release("https://home.lan/a.apk", null)), "0.1.0", "https://home.lan"))
    }
}
