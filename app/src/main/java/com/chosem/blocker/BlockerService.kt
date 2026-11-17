package com.chosem.blocker

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.view.accessibility.AccessibilityEvent

class BlockerService : AccessibilityService() {
    override fun onAccessibilityEvent(e: AccessibilityEvent?) {
        if (e == null || e.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        val pkg = e.packageName?.toString() ?: return
        if (pkg == packageName) return
        val p = getSharedPreferences("b", MODE_PRIVATE)
        if (!p.getBoolean("on", true)) return
        val apps = p.getStringSet("apps", emptySet()) ?: emptySet()
        if (pkg in apps) {
            startActivity(
                Intent(this, BlockActivity::class.java)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                    .putExtra("pkg", pkg)
            )
        }
    }

    override fun onInterrupt() {}
}
