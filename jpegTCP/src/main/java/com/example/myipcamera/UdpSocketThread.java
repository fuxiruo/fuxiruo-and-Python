package com.example.myipcamera;

import android.content.Context;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.util.Log;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

public class UdpSocketThread  extends Thread{
    private DatagramSocket ds;
    private int port = 5555;
    private String TAG = "UdpSocketThread";
    private ConcurrentLinkedQueue<ByteArrayOutputStream> queueToSend;
    private InetAddress ip;
    private String mWifiIp;

    public UdpSocketThread(Context context){
        super();
        try {
            ds = new DatagramSocket();
            ip = InetAddress.getByName("255.255.255.255");
            queueToSend = new ConcurrentLinkedQueue<ByteArrayOutputStream>();

            WifiManager wifiManager = (WifiManager) context.getSystemService(Context.WIFI_SERVICE);
            WifiInfo wifiInfo = wifiManager.getConnectionInfo();
            mWifiIp = intIP2StringIP(wifiInfo.getIpAddress());//得到IPV4地址

            Log.d(TAG, "ipAddress: " + mWifiIp);
        } catch (SocketException e) {
            Log.w(TAG, "UdpSocketThread: ", e);
        }catch(Exception e){
            Log.w(TAG, "UdpSocketThread: ", e);
        }
    }

    private String intIP2StringIP(int ip) {
        return (ip & 0xFF) + "." +
                ((ip >> 8) & 0xFF) + "." +
                ((ip >> 16) & 0xFF) + "." +
                (ip >> 24 & 0xFF);
    }

    @Override
    public void run() {
        Log.d(TAG, "run: start");
        while(true){
            if(this.isInterrupted()){
                Log.d(TAG, "run: stop");
                break;
            }
            try {
                Thread.sleep(1000);
                String sTemp = "@" + mWifiIp + "$";
                byte[] header = sTemp.getBytes(StandardCharsets.UTF_8);
                DatagramPacket dp0 = new DatagramPacket(header, header.length, ip, port);
                ds.send(dp0);
            } catch (Exception e){
                Log.e(TAG, "UdpSocketThread runs: ", e);
            }
        }
    }

    public  void trySend(ByteArrayOutputStream bytesToSend){
        try {
            queueToSend.add(bytesToSend);
        }catch (Exception e){
            Log.e(TAG, "trySend: ", e);
        }
    }
}
