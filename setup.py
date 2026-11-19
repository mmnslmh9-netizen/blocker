import base64, os, shutil

u = base64.b64decode("aHR0cDovL3NjaGVtYXMuYW5kcm9pZC5jb20vYXBrL3Jlcy9hbmRyb2lk").decode()
os.makedirs("app/src/main/res/drawable", exist_ok=True)

if os.path.exists("poster.jpg"):
    shutil.copy("poster.jpg", "app/src/main/res/drawable/splash_img.jpg")

icon_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="{u}" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#060B19" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#003566" android:strokeColor="#00D2FF" android:strokeWidth="3.5" android:pathData="M54,18 L82,30 V54 C82,73 69,86 54,92 C39,86 26,73 26,54 V30 Z"/>
    <path android:fillColor="#0077B6" android:pathData="M54,24 L76,34 V54 C76,69 65,80 54,85 C43,80 32,69 32,54 V34 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M54,43 A6,6 0 1,0 54,55 A6,6 0 1,0 54,43 Z M50,53 L58,53 L60,67 L48,67 Z"/>
</vector>'''

manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="{u}">
    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
    </queries>
    <application
        android:icon="@drawable/ic_launcher"
        android:label="חוסם תכנים"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity android:name=".SplashActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".MainActivity" android:exported="true" />
        <activity android:name=".BlockActivity" android:exported="false" android:excludeFromRecents="true" android:launchMode="singleTask" />
        <service android:name=".BlockerService" android:exported="true" android:label="חוסם תכנים" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_service_config" />
        </service>
        <receiver android:name=".AdminReceiver" android:exported="true" android:permission="android.permission.BIND_DEVICE_ADMIN">
            <meta-data android:name="android.app.device_admin" android:resource="@xml/device_admin" />
            <intent-filter>
                <action android:name="android.app.action.DEVICE_ADMIN_ENABLED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>'''

splash_kt = '''package com.chosem.blocker
import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.os.*
import android.view.Gravity
import android.widget.*

class SplashActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val resId = resources.getIdentifier("splash_img", "drawable", packageName)
        if (resId != 0) {
            val iv = ImageView(this).apply {
                setImageResource(resId)
                scaleType = ImageView.ScaleType.FIT_CENTER
                setBackgroundColor(Color.parseColor("#060B19"))
            }
            setContentView(iv)
        } else {
            val r = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setBackgroundColor(Color.parseColor("#060B19"))
                gravity = Gravity.CENTER
            }
            r.addView(ImageView(this).apply { setImageResource(R.drawable.ic_launcher) }, LinearLayout.LayoutParams(320, 320))
            setContentView(r)
        }
        Handler(Looper.getMainLooper()).postDelayed({
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        }, 1800)
    }
}'''

acc = f'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="{u}"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows|flagReportViewIds"
    android:canRetrieveWindowContent="true"
    android:notificationTimeout="100" />'''

admin_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<device-admin xmlns:android="{u}">
    <uses-policies>
        <force-lock />
    </uses-policies>
</device-admin>'''

admin_kt = '''package com.chosem.blocker
import android.app.admin.DeviceAdminReceiver
class AdminReceiver : DeviceAdminReceiver()'''

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

        val isProtectedSettings = (p == "com.android.settings" || p == "com.google.android.packageinstaller" || p == "com.samsung.android.packageinstaller") &&
            (e.text?.any {
                val s = it.toString()
                s.contains("חוסם תכנים") || s.contains("מנהלי מכשיר") || s.contains("Device admin") || s.contains("יישומים מותקנים") || s.contains("Installed apps")
            } == true)

        val blocked = pr.getStringSet("blocked_apps", emptySet()) ?: emptySet()
        if (!blocked.contains(p) && !isProtectedSettings) return

        val target = if (isProtectedSettings) "settings_guard" else p
        if (target == uPkg && System.currentTimeMillis() - uTime < 60000L) return

        if (System.currentTimeMillis() - last > 700L) {
            last = System.currentTimeMillis()
            performGlobalAction(GLOBAL_ACTION_HOME)
            try {
                startActivity(Intent(this, BlockActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
                    putExtra("pkg", target)
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
            text = if (pkg == "settings_guard") "🔒 הגדרות מוגנות" else "🛡️ אפליקציה נעולה"
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
            text = "פתיחה"
            setTextColor(Color.WHITE)
            background = GradientDrawable().apply {
                setColor(Color.parseColor("#00B4D8"))
                cornerRadius = 24f
            }
            setOnClickListener {
                if (inp.text.toString().trim() == pin) {
                    BlockerService.uPkg = pkg
                    BlockerService.uTime = System.currentTimeMillis()
                    if (pkg != "settings_guard") {
                        packageManager.getLaunchIntentForPackage(pkg)?.let { startActivity(it) }
                    }
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

open("app/src/main/res/drawable/ic_launcher.xml", "w").write(icon_xml)
open("app/src/main/AndroidManifest.xml", "w").write(manifest)
open("app/src/main/res/xml/accessibility_service_config.xml", "w").write(acc)
open("app/src/main/res/xml/device_admin.xml", "w").write(admin_xml)
