package com.example.myipcamera;

import android.util.Log;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;

public class UdpSocketThread  extends Thread{
    private DatagramSocket ds;
    private int port = 10000;
    private String TAG = "UdpSocketThread";
    private ConcurrentLinkedQueue<ByteArrayOutputStream> queueToSend;
    private InetAddress ip;

    public UdpSocketThread(){
        super();
        try {
            ds = new DatagramSocket();
            ip = InetAddress.getByName("255.255.255.255");
            queueToSend = new ConcurrentLinkedQueue<ByteArrayOutputStream>();
        } catch (SocketException e) {
            Log.w(TAG, "UdpSocketThread: ", e);
        }catch(Exception e){
            Log.w(TAG, "UdpSocketThread: ", e);
        }
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
                Thread.sleep(10);
                if(queueToSend.size() > 0){
                    try {
                        ByteArrayOutputStream bos = queueToSend.poll();
                        Log.d(TAG, "send:" + bos.toByteArray().length);
                        byte[] bytesToSend = bos.toByteArray();
                        int j = 1000;
                        int sendCount = 0;
                        ByteArrayInputStream bi = new ByteArrayInputStream(bytesToSend);
                        byte[] header = new byte[8];
                        header[0] = (byte)(0xAA);
                        header[1] = (byte)(0x55);
                        header[2] = (byte)(0xAA);
                        header[3] = (byte)(0x55);
                        header[4] = (byte)((bytesToSend.length >> 24) & 0xFF);
                        header[5] = (byte)((bytesToSend.length >> 16) & 0xFF);
                        header[6] = (byte)((bytesToSend.length >> 8) & 0xFF);
                        header[7] = (byte)(bytesToSend.length & 0xFF);
                        DatagramPacket dp0 = new DatagramPacket(header, header.length, ip, 10000);
                        ds.send(dp0);

                        while(sendCount < bytesToSend.length){
                            byte[] bs = new byte[j];
                            if(j > bytesToSend.length-sendCount){
                                j = bytesToSend.length-sendCount;
                            }
                            int readCount = bi.read(bs, 0, j);
                            sendCount += readCount;
//                            Log.d(TAG, "send: " + readCount + " total:" + sendCount + " all:" + bytesToSend.length + " readCount:"+readCount);
                            DatagramPacket dp = new DatagramPacket(bs, readCount, ip, 10000);
                            ds.send(dp);
                        }
                        Log.d(TAG, "run: send end packet");
                    } catch (Exception e) {
                        Log.e(TAG, "run1: ", e);
                    }
                }
            } catch (Exception e){
                Log.e(TAG, "run2: ", e);
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
