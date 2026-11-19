package com.chosem.blocker

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.provider.Settings
import android.text.InputType
import android.text.TextUtils
import android.view.Gravity
import android.widget.*

class MainActivity : Activity() {

    private lateinit var prefs: android.content.SharedPreferences
    private lateinit var statusText: TextView
    private lateinit var activeSwitch: Switch
    private val selectedPackages = mutableSetOf<String>()
    private var isUnlocked = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prefs = getSharedPreferences("blocker_prefs", Context.MODE_PRIVATE)
        selectedPackages.addAll(prefs.getStringSet("blocked_apps", emptySet()) ?: emptySet())
        checkPinAndLoad()
    }

    private fun checkPinAndLoad() {
        val savedPin = prefs.getString("user_pin", null)
        if (isUnlocked) {
            buildMainUI()
            return
        }

        val input = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            hint = if (savedPin == null) "בחר קוד חדש (4 ספרות)" else "הזן את הקוד שלך"
            gravity = Gravity.CENTER
            textSize = 22f
        }

        val title = if (savedPin == null) "הגדרת קוד נעילה" else "האפליקציה נעולה"
        val message = if (savedPin == null) "בחר סיסמה שתמנע כיבוי של החסימה:" else "הזן קוד PIN כדי להיכנס להגדרות:"

        AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(message)
            .setView(input)
            .setCancelable(false)
            .setPositiveButton("אישור") { _, _ ->
                val entered = input.text.toString().trim()
                if (savedPin == null) {
                    if (entered.length >= 4) {
                        prefs.edit().putString("user_pin", entered).apply()
                        isUnlocked = true
                        buildMainUI()
                    } else {
                        Toast.makeText(this, "יש להזין לפחות 4 ספרות", Toast.LENGTH_SHORT).show()
                        checkPinAndLoad()
                    }
                } else {
                    if (entered == savedPin) {
                        isUnlocked = true
                        buildMainUI()
                    } else {
                        Toast.makeText(this, "קוד שגוי!", Toast.LENGTH_SHORT).show()
                        checkPinAndLoad()
                    }
                }
            }
            .setNegativeButton("יציאה") { _, _ -> finish() }
            .show()
    }

    private fun buildMainUI() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#0B132B"))
            setPadding(40, 50, 40, 30)
        }

        val header = TextView(this).apply {
            text = "חוסם תכנים"
            textSize = 28f
            setTextColor(Color.parseColor("#4EA8DE"))
            gravity = Gravity.END
        }
        root.addView(header)

        statusText = TextView(this).apply {
            textSize = 16f
            gravity = Gravity.END
            setPadding(0, 12, 0, 20)
        }
        root.addView(statusText)

        val btnAccessibility = Button(this).apply {
            text = "שלב 1: הפעל את שירות החסימה"
            setBackgroundColor(Color.parseColor("#3A506B"))
            setTextColor(Color.WHITE)
            setOnClickListener {
                startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            }
        }
        root.addView(btnAccessibility)

        activeSwitch = Switch(this).apply {
            text = "חסימה פעילה"
            textSize = 20f
            setTextColor(Color.WHITE)
            isChecked = prefs.getBoolean("is_active", false)
            setPadding(0, 30, 0, 30)
            setOnCheckedChangeListener { _, isChecked ->
                prefs.edit().putBoolean("is_active", isChecked).apply()
                Toast.makeText(
                    this@MainActivity,
                    if (isChecked) "החסימה הופעלה!" else "החסימה כובתה",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
        root.addView(activeSwitch)

        val btnChangePin = Button(this).apply {
            text = "שינוי קוד PIN"
            setBackgroundColor(Color.parseColor("#1C2541"))
            setTextColor(Color.LTGRAY)
            setOnClickListener {
                prefs.edit().remove("user_pin").apply()
                isUnlocked = false
                checkPinAndLoad()
            }
        }
        root.addView(btnChangePin)

        val subTitle = TextView(this).apply {
            text = "סמן את האפליקציות שייחסמו:"
            textSize = 18f
            setTextColor(Color.WHITE)
            gravity = Gravity.END
            setPadding(0, 30, 0, 15)
        }
        root.addView(subTitle)

        val scroll = ScrollView(this)
        val listLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }

        val pm = packageManager
        val apps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            .filter { pm.getLaunchIntentForPackage(it.packageName) != null && it.packageName != packageName }
            .sortedBy { pm.getApplicationLabel(it).toString().lowercase() }

        for (app in apps) {
            val cb = CheckBox(this).apply {
                text = pm.getApplicationLabel(app).toString()
                setTextColor(Color.WHITE)
                textSize = 17f
                isChecked = selectedPackages.contains(app.packageName)
                setPadding(10, 18, 10, 18)
                setOnCheckedChangeListener { _, checked ->
                    if (checked) selectedPackages.add(app.packageName)
                    else selectedPackages.remove(app.packageName)
                    prefs.edit().putStringSet("blocked_apps", selectedPackages.toSet()).apply()
                }
            }
            listLayout.addView(cb)
        }

        scroll.addView(listLayout)
        root.addView(scroll)
        setContentView(root)
        updateServiceStatus()
    }

    override fun onResume() {
        super.onResume()
        if (::statusText.isInitialized) {
            updateServiceStatus()
        }
    }

    private fun updateServiceStatus() {
        val enabled = isAccessibilityServiceEnabled()
        statusText.text = if (enabled) "שירות החסימה פעיל ✓" else "שירות החסימה כבוי ✗ (לחץ על שלב 1)"
        statusText.setTextColor(if (enabled) Color.parseColor("#52B788") else Color.parseColor("#F4A261"))
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val expected = "$packageName/${BlockerService::class.java.canonicalName}"
        val enabledServices = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES) ?: return false
        val splitter = TextUtils.SimpleStringSplitter(':')
        splitter.setString(enabledServices)
        while (splitter.hasNext()) {
            if (splitter.next().equals(expected, ignoreCase = true)) return true
        }
        return false
    }
}
