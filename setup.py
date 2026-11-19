import base64

u = base64.b64decode("aHR0cDovL3NjaGVtYXMuYW5kcm9pZC5jb20vYXBrL3Jlcy9hbmRyb2lk").decode()

manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="{u}">
    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
    </queries>
    <application
        android:label="חוסם תכנים"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".BlockActivity" android:exported="false" android:excludeFromRecents="true" android:launchMode="singleTask" />
        <service android:name=".BlockerService" android:exported="true" android:label="חוסם תכנים" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_service_config" />
        </service>
    </application>
</manifest>'''

acc = f'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="{u}"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows|flagReportViewIds"
    android:canRetrieveWindowContent="true"
    android:notificationTimeout="100" />'''

service_kt = '''package com.chosem.blocker
import android.accessibilityservice.AccessibilityService
import android.content.*
import android.view.accessibility.AccessibilityEvent

class BlockerService : AccessibilityService() {
    companion object {
        var uPkg: String? = null
        var uTime = 0L
    }
    private var last = 0L

    override fun onAccessibilityEvent(e: AccessibilityEvent?) {
        val p = e?.packageName?.toString() ?: return
        if (p == "com.chosem.blocker" || p == packageName || p == "com.android.systemui" || p.contains("launcher")) return
        val pr = getSharedPreferences("blocker_prefs", 0)
        if (!pr.getBoolean("is_active", false)) return
        val blocked = pr.getStringSet("blocked_apps", emptySet()) ?: emptySet()
        if (!blocked.contains(p)) return
        if (p == uPkg && System.currentTimeMillis() - uTime < 60000L) return
        if (System.currentTimeMillis() - last > 700L) {
            last = System.currentTimeMillis()
            performGlobalAction(GLOBAL_ACTION_HOME)
            try {
                startActivity(Intent(this, BlockActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                    putExtra("pkg", p)
                })
            } catch (_: Exception) {}
        }
    }
    override fun onInterrupt() {}
}'''

block_kt = '''package com.chosem.blocker
import android.app.Activity
import android.graphics.*
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.widget.*

class BlockActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val pkg = intent.getStringExtra("pkg") ?: ""
        val pin = getSharedPreferences("blocker_prefs", 0).getString("user_pin", "1234") ?: "1234"
        val r = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#060B19"))
            gravity = Gravity.CENTER
            setPadding(60, 60, 60, 60)
        }
        val c = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(50, 60, 50, 60)
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#0F1B38"))
                cornerRadius = 40f
                setStroke(4, Color.parseColor("#00D2FF"))
            }
        }
        c.addView(TextView(this).apply {
            text = "🛡️ אפליקציה נעולה"
            textSize = 25f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        })
        c.addView(TextView(this).apply {
            text = "הזן קוד PIN לפתיחה:"
            textSize = 15f
            setTextColor(Color.parseColor("#90E0EF"))
            gravity = Gravity.CENTER
            setPadding(0, 12, 0, 28)
        })
        val inp = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            hint = "••••"
            setHintTextColor(Color.GRAY)
            setTextColor(Color.WHITE)
            textSize = 24f
            gravity = Gravity.CENTER
        }
        c.addView(inp)
        c.addView(Button(this).apply {
            text = "פתיחת אפליקציה"
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#00B4D8"))
                cornerRadius = 24f
            }
            setOnClickListener {
                if (inp.text.toString().trim() == pin) {
                    BlockerService.uPkg = pkg
                    BlockerService.uTime = System.currentTimeMillis()
                    packageManager.getLaunchIntentForPackage(pkg)?.let { startActivity(it) }
                    finish()
                } else {
                    Toast.makeText(this@BlockActivity, "קוד שגוי", Toast.LENGTH_SHORT).show()
                }
            }
        })
        r.addView(c)
        setContentView(r)
    }
    override fun onBackPressed() { moveTaskToBack(true); finish() }
}'''

open("app/src/main/AndroidManifest.xml", "w").write(manifest)
open("app/src/main/res/xml/accessibility_service_config.xml", "w").write(acc)
open("app/src/main/java/com/chosem/blocker/BlockerService.kt", "w").write(service_kt)
open("app/src/main/java/com/chosem/blocker/BlockActivity.kt", "w").write(block_kt)
import setup2
