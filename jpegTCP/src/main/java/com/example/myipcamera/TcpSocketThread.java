package com.example.myipcamera;

import android.util.Log;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.DatagramPacket;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.concurrent.ConcurrentLinkedQueue;

class ClientThread implements Runnable {
    private String TAG = "ClientThread";
    private Socket mClientSocket;
    private OutputStream outputStream;    //声明输出流
    private InputStream inputStream;    //声明输入流
    private BufferedReader reader;        //声明缓冲流，用于读取接收的数据
    private ConcurrentLinkedQueue<ByteArrayOutputStream> queueToSend;

    ClientThread(Socket clientSocket) throws SocketException {
        mClientSocket = clientSocket;
        mClientSocket.setSoTimeout(10);  //设置超时时间10毫秒
        queueToSend = new ConcurrentLinkedQueue<ByteArrayOutputStream>();
    }

    public  boolean trySend(ByteArrayOutputStream bytesToSend){
        try {
            if(mClientSocket.isClosed()){
                Log.d(TAG, "trySend: socket close");
                return false;
            }else{
                queueToSend.add(bytesToSend);
                return true;
            }
        }catch (Exception e){
            Log.e(TAG, "trySend: ", e);
            return false;
        }
    }

    public static String BytesToString(byte[] bytes) {
        StringBuilder strBuilder = new StringBuilder();
        for (int i = 0; i < bytes.length; i++) {
            if (bytes[i] != 0) {
                strBuilder.append((char) bytes[i]);
            } else{
                break;
            }
        }
        return strBuilder.toString();
    }

    public  void stop(){
        try {
            mClientSocket.close();
        } catch (IOException e) {
            Log.w(TAG, e);
        }
    }

    private void Swipe(){
        Process ps = null;
        try {
            ps = Runtime.getRuntime().exec("input swipe 500 800 500 400\n");
            Log.d(TAG,"process " + ps.toString());
        } catch (IOException e) {
            Log.e(TAG, "Swipe: ", e);
        }
    }
/*
* 在Socket对象被关闭后，我们可以通过isClosed方法来判断某个Socket对象是否处于关闭状态。
* 然而使用isClosed方法所返回的只是Socket对象的当前状态，也就是说，不管Socket对象是否曾经连接成功过，只要处于关闭状态，isClosde就返回true。
* 如果只是建立一个未连接的Socket对象，isClose也同样返回true。如下面的代码将输出false
* 除了isClose方法，Socket类还有一个isConnected方法来判断Socket对象是否连接成功。看到这个名字，也许读者会产生误解。其实isConnected方法所判断的并不是Socket对象的当前连接状态，
* 而是Socket对象是否曾经连接成功过，如果成功连接过，即使现在isClose返回true，isConnected仍然返回true。
* 因此，要判断当前的Socket对象是否处于连接状态，必须同时使用isClose和isConnected方法，即只有当isClose返回false，isConnected返回true的时候Socket对象才处于连接状态。
* */
    @Override
    public void run() {
        try {
            inputStream = mClientSocket.getInputStream();    //获取套接字输入流
            //根据输入流创建BufferedReader对象（用于读取数据）
            reader = new BufferedReader(new InputStreamReader(inputStream));

            outputStream = mClientSocket.getOutputStream();
        } catch (IOException e) {
            Log.w(TAG, "IOException: ", e);
        }

        try{
            while (mClientSocket.isConnected() && !mClientSocket.isClosed()){
                InputStream ins = mClientSocket.getInputStream();
                byte[] bytes = new byte[1024];
                Arrays.fill(bytes, (byte) 0);
                try {
    //                    Log.d(TAG, "try data read");
                    if(ins.read(bytes) != -1) {
                        Log.d(TAG,mClientSocket.getRemoteSocketAddress().toString() + "客户端的信息：" + BytesToString(bytes));    //将接收的信息输出
                        //Swipe();
                    }else{
                        Log.d(TAG, mClientSocket.getRemoteSocketAddress().toString() + " close");
                        break;
                    }
                }catch (SocketTimeoutException e){
                    //Log.d(TAG, "SocketTimeoutException:", e);
                }

                if(queueToSend.size() > 0){
                    ByteArrayOutputStream bos = queueToSend.poll();
//                    Log.d(TAG, "send:" + bos.toByteArray().length);
                    byte[] bytesToSend = bos.toByteArray();
                    byte[] header = new byte[8];
                    header[0] = (byte)(0xAA);
                    header[1] = (byte)(0x55);
                    header[2] = (byte)(0xAA);
                    header[3] = (byte)(0x55);
                    header[4] = (byte)((bytesToSend.length >> 24) & 0xFF);
                    header[5] = (byte)((bytesToSend.length >> 16) & 0xFF);
                    header[6] = (byte)((bytesToSend.length >> 8) & 0xFF);
                    header[7] = (byte)(bytesToSend.length & 0xFF);
                    outputStream.write(header, 0, header.length);
                    outputStream.flush();
                    outputStream.write(bytesToSend, 0, bytesToSend.length);
                    outputStream.flush();
//                    Log.d(TAG, "run: send end packet");
                }
            }
        } catch (Exception e){
            Log.w(TAG, "Exception: ", e);
        }

        try {
            mClientSocket.close();
        } catch (IOException e) {
            Log.d(TAG, "close fail: ", e);
        }
        Log.d(TAG, "close: " + mClientSocket.getRemoteSocketAddress().toString() );
    }
}

public class TcpSocketThread  extends Thread{
    private String TAG = "TcpSocketThread";
    private ServerSocket mServer;
    private ArrayList<ClientThread> mClientList = new ArrayList<>();

    public TcpSocketThread(int port){
        try {
            mServer = new ServerSocket(port);
            Log.d(TAG, "TcpServer start");
        } catch (IOException e) {
            Log.w(TAG, "IOException: ", e);
        }catch(Exception e){
            Log.w(TAG, "Exception: ", e);
        }
    }

    @Override
    public void run() {
        while(true) {
            if (this.isInterrupted()) {
                Log.d(TAG, "run: stop");
                break;
            }

            Log.d(TAG, "等待设备连接");
            try {
                final Socket socket = mServer.accept();
                // 获取手机连接的地址及端口号
                final String address = socket.getRemoteSocketAddress().toString();
                Log.d(TAG, "连接成功，连接的设备为：" + address);

                ClientThread clientThread = new ClientThread(socket);
                mClientList.add(clientThread);
                // Runs the thread (calls its run method)
                new Thread(clientThread).start();
            } catch (IOException e) {
                Log.w(TAG, "IOException: ", e);
            }
        }
    }

    public  void trySend(ByteArrayOutputStream bytesToSend){
        try {
            Iterator it = mClientList.iterator();
            while(it.hasNext()){
                ClientThread thread = (ClientThread) it.next();
                if(!thread.trySend(bytesToSend)){
                    Log.d(TAG, "trySend: fail,remove it");
                    it.remove();
                }
            }
        }catch (Exception e){
            Log.d(TAG, "trySend: " + e);
        }
    }

    public void stopListen(){
        try {
            for (ClientThread thread : mClientList) {
                thread.stop();
            }
            mServer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void finalize() throws Throwable {
        Log.d(TAG, "finalize");
        stopListen();
        super.finalize();
    }
}
