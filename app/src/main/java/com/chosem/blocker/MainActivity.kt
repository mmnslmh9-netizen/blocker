package com.chosem.blocker

import android.app.*
import android.content.*
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.provider.Settings
import android.text.InputType
import android.view.Gravity
import android.widget.*

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("blocker_prefs", Context.MODE_PRIVATE)
        val savedPin = prefs.getString("user_pin", null)
        val input = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            hint = if (savedPin == null) "בחר קוד חדש (4 ספרות)" else "הזן קוד PIN"
            gravity = Gravity.CENTER
        }
        AlertDialog.Builder(this)
            .setTitle(if (savedPin == null) "הגדרת קוד נעילה" else "האפליקציה נעולה")
            .setView(input)
            .setCancelable(false)
            .setPositiveButton("אישור") { _, _ ->
                val code = input.text.toString().trim()
                if (savedPin == null && code.length >= 4) {
                    prefs.edit().putString("user_pin", code).apply()
                    showUI(prefs)
                } else if (code == savedPin) {
                    showUI(prefs)
                } else {
                    Toast.makeText(this, "קוד שגוי (מינימום 4 ספרות)", Toast.LENGTH_SHORT).show()
                    recreate()
                }
            }
            .setNegativeButton("יציאה") { _, _ -> finish() }
            .show()
    }

    private fun showUI(prefs: SharedPreferences) {
        val selected = (prefs.getStringSet("blocked_apps", emptySet()) ?: emptySet()).toMutableSet()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#0B132B"))
            setPadding(40, 50, 40, 30)
        }
        root.addView(Button(this).apply {
            text = "שלב 1: הפעל שירות חסימה בהגדרות"
            setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
        })
        root.addView(Switch(this).apply {
            text = "חסימה פעילה"
            textSize = 20f
            setTextColor(Color.WHITE)
            isChecked = prefs.getBoolean("is_active", false)
            setPadding(0, 25, 0, 25)
            setOnCheckedChangeListener { _, on -> prefs.edit().putBoolean("is_active", on).apply() }
        })
        val scroll = ScrollView(this)
        val list = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        val pm = packageManager
        pm.getInstalledApplications(PackageManager.GET_META_DATA)
            .filter { pm.getLaunchIntentForPackage(it.packageName) != null && it.packageName != packageName }
            .sortedBy { pm.getApplicationLabel(it).toString().lowercase() }
            .forEach { app ->
                list.addView(CheckBox(this).apply {
                    text = pm.getApplicationLabel(app).toString()
                    setTextColor(Color.WHITE)
                    isChecked = selected.contains(app.packageName)
                    setOnCheckedChangeListener { _, chk ->
                        if (chk) selected.add(app.packageName) else selected.remove(app.packageName)
                        prefs.edit().putStringSet("blocked_apps", selected.toSet()).apply()
                    }
                })
            }
        scroll.addView(list)
        root.addView(scroll)
        setContentView(root)
    }
}
