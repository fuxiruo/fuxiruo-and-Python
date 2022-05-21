package com.example.myipcamera;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.hardware.Camera;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.FrameLayout;

import java.io.DataOutputStream;
import java.io.IOException;

public class MainActivity extends Activity {
    private Camera mCamera;
    public MyCameraView mPreview;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mCamera = getDefaultFrontFacingCameraInstance();
        mPreview = new MyCameraView(this, mCamera);
        FrameLayout preview = (FrameLayout) findViewById(R.id.frameLayout);
        preview.addView(mPreview);
    }

    private static Camera getDefaultCamera(int position) {
        // Find the total number of cameras available
        int  mNumberOfCameras = Camera.getNumberOfCameras();

        // Find the ID of the back-facing ("default") camera
        Camera.CameraInfo cameraInfo = new Camera.CameraInfo();
        for (int i = 0; i < mNumberOfCameras; i++) {
            Camera.getCameraInfo(i, cameraInfo);
            if (cameraInfo.facing == position) {
                return Camera.open(i);

            }
        }

        return null;
    }

    public static Camera getDefaultFrontFacingCameraInstance() {
        return getDefaultCamera(Camera.CameraInfo.CAMERA_FACING_FRONT);
    }

    public void onClick(View v)
    {
        finish();
        mCamera.release();
        mCamera=null;
    }

    // 使得点击屏幕的任何地方不会退出该活动
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        return false;
    }
}