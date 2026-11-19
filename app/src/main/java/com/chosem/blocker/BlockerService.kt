package com.chosem.blocker

import android.accessibilityservice.AccessibilityService
import android.content.Context
import android.content.Intent
import android.view.accessibility.AccessibilityEvent

class BlockerService : AccessibilityService() {

    private var lastBlockTime = 0L

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val pkg = event?.packageName?.toString() ?: return
        if (pkg == packageName || pkg == "com.android.systemui" || pkg.contains("launcher")) return

        val prefs = getSharedPreferences("blocker_prefs", Context.MODE_PRIVATE)
        val isActive = prefs.getBoolean("is_active", false)
        if (!isActive) return

        val blockedApps = prefs.getStringSet("blocked_apps", emptySet()) ?: emptySet()

        if (blockedApps.contains(pkg)) {
            val now = System.currentTimeMillis()
            if (now - lastBlockTime > 600) {
                lastBlockTime = now
                performGlobalAction(GLOBAL_ACTION_HOME)
                try {
                    val intent = Intent(this, BlockActivity::class.java).apply {
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                    }
                    startActivity(intent)
                } catch (_: Exception) {
                }
            }
        }
    }

    override fun onInterrupt() {}
}
