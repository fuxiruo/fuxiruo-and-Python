package com.example.myipcamera;

import android.content.Context;
import android.graphics.ImageFormat;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.YuvImage;
import android.hardware.Camera;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.List;

public class MyCameraView  extends SurfaceView implements SurfaceHolder.Callback,Camera.PreviewCallback {
    private SurfaceHolder mHolder;
    private Camera mCamera;
    private String TAG = "MyCameraView";
    private int width;
    private int height;
    private UdpSocketThread ust;
    private  TcpSocketThread tst;

    public MyCameraView(Context context, Camera camera) {
        super(context);
        Log.d(TAG, "MyCameraView: ");
        mCamera = camera;
        ust = new UdpSocketThread();
        tst = new TcpSocketThread(6666);

        // Install a SurfaceHolder.Callback so we get notified when the
        // underlying surface is created and destroyed.
        mHolder = getHolder();
        mHolder.addCallback(this);
        // deprecated setting, but required on Android versions prior to 3.0
        mHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
    }

    public void surfaceCreated(SurfaceHolder holder) {
        Log.d(TAG, "surfaceCreated: ");
        // The Surface has been created, now tell the camera where to draw the preview.
        try {
            ust.start();
            tst.start();

            mCamera.setDisplayOrientation(90);
            mCamera.setPreviewCallback(this);
            mCamera.setPreviewDisplay(holder);
            mCamera.startPreview();
        } catch (IOException e) {
            Log.w(TAG, "Error setting camera preview: " + e.getMessage());
        }
    }

    public void surfaceDestroyed(SurfaceHolder holder) {
        // empty. Take care of releasing the Camera preview in your activity.
        Log.d(TAG, "surfaceDestroyed: ");
        ust.interrupt();
        tst.stopListen();
        tst.interrupt();
    }

    public void surfaceChanged(SurfaceHolder holder, int format, int w, int h) {
        // If your preview can change or rotate, take care of those events here.
        // Make sure to stop the preview before resizing or reformatting it.

        if (mHolder.getSurface() == null){
            // preview surface does not exist
            return;
        }
        Log.d(TAG, "surfaceChanged");

        // stop preview before making changes
        try {
            mCamera.stopPreview();
        } catch (Exception e){
            // ignore: tried to stop a non-existent preview
        }

        // set preview size and make any resize, rotate or
        // reformatting changes here

        // start preview with new settings
        try {
            //Configration Camera Parameter(full-size)
            Camera.Parameters parameters = mCamera.getParameters();
            parameters.setPreviewSize(640,480);
            parameters.setPreviewFpsRange(15000, 15000);
//            List<int[]> range=parameters.getSupportedPreviewFpsRange();
//            Log.d(TAG, "range:"+range.size());
//            for(int i=0; i<range.size(); i++){
//                int[] r=range.get(i);
//                for(int k=0;k< r.length; k++){
//                    Log.d(TAG, TAG+r[k]);
//                }
//            }

            this.width=parameters.getPreviewSize().width;
            this.height=parameters.getPreviewSize().height;
            mCamera.setParameters(parameters);
            //mCamera.setDisplayOrientation(90);
            mCamera.setPreviewCallback(this);
            mCamera.setPreviewDisplay(mHolder);
            mCamera.startPreview();
            Log.d(TAG, "start preview");

        } catch (Exception e){
            Log.w(TAG, "Error starting camera preview: " + e.getMessage());
        }
    }

    public void onPreviewFrame(byte[] data,Camera camera){
        try{
            if(data == null){
                Log.w(TAG, "data null ");
                return;
            }
            //convert YuvImage(NV21) to JPEG Image data
            //Log.d(TAG, "onPreviewFrame: ");

            //convert YuvImage(NV21) to JPEG Image data
            YuvImage yuvimage=new YuvImage(data, ImageFormat.NV21,this.width,this.height,null);
            //Log.d(TAG, "WidthandHeight"+yuvimage.getHeight()+"::"+yuvimage.getWidth());
            ByteArrayOutputStream baos=new ByteArrayOutputStream();
            yuvimage.compressToJpeg(new Rect(0,0,this.width,this.height),100,baos);

            tst.trySend(baos);
        }catch(Exception e){
            Log.d(TAG,e.toString());
        }
    }
}
