package com.chosem.blocker

import android.app.Activity
import android.content.Intent
import android.content.SharedPreferences
import android.graphics.Color
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.*

class MainActivity : Activity() {
    private lateinit var p: SharedPreferences
    private lateinit var status: TextView
    private val sel = mutableSetOf<String>()
    private val boxes = mutableMapOf<String, CheckBox>()
    private val preset = listOf(
        "com.zhiliaoapp.musically", "com.ss.android.ugc.trill", "org.telegram.messenger", "org.telegram.messenger.web",
        "org.thunderdog.challegram", "com.instagram.android", "com.facebook.katana", "com.snapchat.android",
        "com.twitter.android", "com.reddit.frontpage", "com.discord", "com.pinterest"
    )

    private fun save() { p.edit().putStringSet("apps", HashSet(sel)).apply() }

    private fun tv(t: String, size: Float, color: Int = Color.WHITE) = TextView(this).apply {
        text = t; textSize = size; setTextColor(color); setPadding(0, 12, 0, 12)
    }

    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        p = getSharedPreferences("b", MODE_PRIVATE)
        sel.addAll(p.getStringSet("apps", emptySet()) ?: emptySet())
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 70, 40, 40)
            layoutDirection = View.LAYOUT_DIRECTION_RTL
        }
        root.addView(tv("חוסם תכנים", 34f, Color.parseColor("#2fb4ff")))
        status = tv("", 16f)
        root.addView(status)
        root.addView(Button(this).apply {
            text = "שלב 1: הפעל את שירות החסימה"
            setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
        })
        root.addView(Switch(this).apply {
            text = "חסימה פעילה"; textSize = 20f; setTextColor(Color.WHITE)
            isChecked = p.getBoolean("on", true); setPadding(0, 24, 0, 24)
            setOnCheckedChangeListener { _, c -> p.edit().putBoolean("on", c).apply() }
        })
        root.addView(tv("שלב 2: סמן את האפליקציות שיהיו חסומות", 18f))
        root.addView(Button(this).apply {
            text = "סמן רשתות חברתיות וטיקטוק וטלגרם"
            setOnClickListener { for ((k, c) in boxes) if (k in preset) c.isChecked = true }
        })
        val pm = packageManager
        val apps = pm.queryIntentActivities(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
            .map { it.activityInfo.packageName to it.loadLabel(pm).toString() }
            .filter { it.first != packageName }
            .distinctBy { it.first }
            .sortedBy { it.second.lowercase() }
        for ((pkg, label) in apps) {
            val cb = CheckBox(this).apply {
                text = label; textSize = 17f; setTextColor(Color.WHITE)
                isChecked = pkg in sel
                setOnCheckedChangeListener { _, c -> if (c) sel.add(pkg) else sel.remove(pkg); save() }
            }
            boxes[pkg] = cb
            root.addView(cb)
        }
        setContentView(ScrollView(this).apply {
            setBackgroundColor(Color.parseColor("#030816")); addView(root)
        })
    }

    override fun onResume() {
        super.onResume()
        val en = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES) ?: ""
        val on = en.contains(packageName)
        status.text = if (on) "שירות החסימה פעיל ✓" else "שירות החסימה כבוי. לחץ על הכפתור ובחר 'חוסם תכנים'"
        status.setTextColor(if (on) Color.parseColor("#3df57a") else Color.parseColor("#ff5a5a"))
    }
}
