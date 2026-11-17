package com.chosem.blocker

import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class BlockActivity : Activity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val pkg = intent.getStringExtra("pkg") ?: ""
        val name = try { packageManager.getApplicationLabel(packageManager.getApplicationInfo(pkg, 0)).toString() } catch (e: Exception) { pkg }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(60, 60, 60, 60)
            setBackgroundColor(Color.parseColor("#2a0000"))
        }
        root.addView(TextView(this).apply { text = "⛔"; textSize = 90f; gravity = Gravity.CENTER })
        root.addView(TextView(this).apply {
            text = "חסום"; textSize = 52f; setTextColor(Color.WHITE); gravity = Gravity.CENTER
            setTypeface(typeface, android.graphics.Typeface.BOLD)
        })
        root.addView(TextView(this).apply {
            text = "האפליקציה \"$name\" חסומה"; textSize = 22f
            setTextColor(Color.parseColor("#ff8a8a")); gravity = Gravity.CENTER; setPadding(0, 20, 0, 50)
        })
        root.addView(Button(this).apply { text = "חזרה למסך הבית"; setOnClickListener { goHome() } })
        setContentView(root)
    }

    private fun goHome() {
        startActivity(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        finish()
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() { goHome() }
}
