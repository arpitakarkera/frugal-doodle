package com.example.arpitakarkera.colorblob;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;

public class Main2Activity extends AppCompatActivity {
    private IntentIntegrator qrScan;
    private String SERVER_IP;
    private Intent intent1;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);

        qrScan = new IntentIntegrator(this);
        qrScan.initiateScan();
//        qrScan.setOrientationLocked(true);


    }



    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        IntentResult result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data);
        if (result != null) {
            //if qrcode has nothing in it
            if (result.getContents() == null) {
                Toast.makeText(this, "Result Not Found", Toast.LENGTH_LONG).show();
            } else {
                //if qr contains data
                SERVER_IP = String.valueOf(result.getContents());
                Toast.makeText(this, SERVER_IP, Toast.LENGTH_SHORT).show();
                intent1 = new Intent (Main2Activity.this,MainActivity.class);
                intent1.putExtra("IP",SERVER_IP);
                startActivity(intent1);
            }
        } else {
            super.onActivityResult(requestCode, resultCode, data);
        }
    }
}
