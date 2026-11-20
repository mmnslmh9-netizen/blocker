main_kt = '''package com.chosem.blocker
import android.app.*
import android.app.admin.DevicePolicyManager
import android.content.*
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.text.InputType
import android.view.Gravity
import android.widget.*

class MainActivity : Activity() {
    private lateinit var pr: SharedPreferences
    private val sel = mutableSetOf<String>()
    private lateinit var dpm: DevicePolicyManager
    private lateinit var comp: ComponentName

    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        pr = getSharedPreferences("blocker_prefs", 0)
        dpm = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        comp = ComponentName(this, AdminReceiver::class.java)
        
        val saved = pr.getStringSet("blocked_apps", emptySet()) ?: emptySet()
        sel.addAll(saved.filter { it != "com.chosem.blocker" && it != packageName })
        pr.edit().putStringSet("blocked_apps", sel.toSet()).apply()
        ask()
    }

    private fun ask() {
        val sp = pr.getString("user_pin", null)
        val inp = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            hint = if (sp == null) "בחר קוד חדש (4 ספרות)" else "הזן קוד PIN"
            gravity = Gravity.CENTER
            textSize = 22f
        }
        AlertDialog.Builder(this)
            .setTitle(if (sp == null) "🛡️ הגדרת קוד נעילה" else "🛡️ חוסם תכנים")
            .setView(inp)
            .setCancelable(false)
            .setPositiveButton("כניסה") { _, _ ->
                val c = inp.text.toString().trim()
                if (sp == null && c.length >= 4) {
                    pr.edit().putString("user_pin", c).apply()
                    ui()
                } else if (c == sp) {
                    ui()
                } else {
                    Toast.makeText(this, "קוד שגוי", Toast.LENGTH_SHORT).show()
                    ask()
                }
            }
            .setNegativeButton("יציאה") { _, _ -> finish() }
            .show()
    }

    private fun bg(s: String = "#1D3557") = GradientDrawable().apply {
        setColor(Color.parseColor("#0F1B38"))
        cornerRadius = 32f
        setStroke(3, Color.parseColor(s))
    }

    private fun ui() {
        val r = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#060B19"))
            setPadding(36, 40, 36, 24)
        }
        val h = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(30, 36, 30, 36)
            background = bg("#00D2FF")
        }
        h.addView(TextView(this).apply {
            text = "🛡️ חוסם תכנים"
            textSize = 28f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        })
        h.addView(Switch(this).apply {
            text = "חסימה פעילה"
            textSize = 20f
            setTextColor(Color.parseColor("#4ADE80"))
            isChecked = pr.getBoolean("is_active", false)
            setPadding(0, 20, 0, 0)
            setOnCheckedChangeListener { _, on -> pr.edit().putBoolean("is_active", on).apply() }
        })
        r.addView(h)

        val btnRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 18, 0, 0)
        }
        btnRow.addView(Button(this).apply {
            text = "⚙️ שירות נגישות"
            textSize = 13f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply { setColor(Color.parseColor("#0077B6")); cornerRadius = 24f }
            setOnClickListener { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }
        }, LinearLayout.LayoutParams(0, -2, 1f).apply { marginEnd = 8 })

        val isAdminActive = dpm.isAdminActive(comp)
        btnRow.addView(Button(this).apply {
            text = if (isAdminActive) "🔒 הגנה פעילה" else "🔒 מניעת מחיקה"
            textSize = 13f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply { 
                setColor(Color.parseColor(if (isAdminActive) "#10B981" else "#0284C7"))
                cornerRadius = 24f 
            }
            setOnClickListener {
                if (!dpm.isAdminActive(comp)) {
                    val i = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN).apply {
                        putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, comp)
                        putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION, "חובה להפעיל כדי למנוע את מחיקת האפליקציה ללא קוד.")
                    }
                    startActivity(i)
                } else {
                    Toast.makeText(this@MainActivity, "ההגנה מפני מחיקה כבר פעילה!", Toast.LENGTH_SHORT).show()
                }
            }
        }, LinearLayout.LayoutParams(0, -2, 1f))
        r.addView(btnRow)

        val cr = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 18, 0, 16)
        }
        val pm = packageManager
        val apps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            .filter { pm.getLaunchIntentForPackage(it.packageName) != null && it.packageName != "com.chosem.blocker" && it.packageName != packageName }
            .sortedBy { pm.getApplicationLabel(it).toString().lowercase() }

        fun cb(t: String, col: String, f: () -> Unit) = Button(this).apply {
            text = t
            textSize = 12f
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply { setColor(Color.parseColor(col)); cornerRadius = 20f }
            setOnClickListener { f(); ui() }
        }
        cr.addView(cb("📱 רשתות", "#1E293B") {
            val s = listOf("tiktok", "musically", "instagram", "facebook", "telegram", "snapchat")
            apps.filter { a -> s.any { a.packageName.contains(it, true) } }.forEach { sel.add(it.packageName) }
            pr.edit().putStringSet("blocked_apps", sel.toSet()).apply()
        }, LinearLayout.LayoutParams(0, -2, 1f).apply { marginEnd = 8 })

        cr.addView(cb("🌐 דפדפנים", "#1E293B") {
            val b = listOf("chrome", "browser", "opera", "firefox", "brave")
            apps.filter { a -> b.any { a.packageName.contains(it, true) } }.forEach { sel.add(it.packageName) }
            pr.edit().putStringSet("blocked_apps", sel.toSet()).apply()
        }, LinearLayout.LayoutParams(0, -2, 1f).apply { marginEnd = 8 })

        cr.addView(cb("🧹 נקה הכל", "#7F1D1D") {
            sel.clear()
            pr.edit().putStringSet("blocked_apps", emptySet()).apply()
        }, LinearLayout.LayoutParams(0, -2, 1f))
        r.addView(cr)

        val sc = ScrollView(this)
        val l = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        for (a in apps) {
            val row = LinearLayout(this).apply {
                setPadding(24, 18, 24, 18)
                background = bg()
            }
            row.addView(CheckBox(this).apply {
                text = "  " + pm.getApplicationLabel(a)
                setTextColor(Color.WHITE)
                textSize = 16f
                isChecked = sel.contains(a.packageName)
                setOnCheckedChangeListener { _, c ->
                    if (c) sel.add(a.packageName) else sel.remove(a.packageName)
                    pr.edit().putStringSet("blocked_apps", sel.toSet()).apply()
                }
            })
            l.addView(row, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = 12 })
        }
        sc.addView(l)
        r.addView(sc)
        setContentView(r)
    }
}'''

open("app/src/main/java/com/chosem/blocker/MainActivity.kt", "w").write(main_kt)
