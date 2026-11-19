package com.chosem.blocker

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.widget.TextView

class BlockActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tv = TextView(this).apply {
            text = "הגישה לאפליקציה זו חסומה"
            textSize = 24f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#0B132B"))
            gravity = Gravity.CENTER
        }
        setContentView(tv)
    }

    override fun onBackPressed() {
        moveTaskToBack(true)
    }
}
