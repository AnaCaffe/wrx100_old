package com.teleofis.wrxconfig.transport;

import java.util.concurrent.TimeUnit;

import jssc.SerialPort;
import jssc.SerialPortEvent;
import jssc.SerialPortEventListener;
import jssc.SerialPortException;

import com.teleofis.utils.concurrency.ManualResetEvent;
import com.teleofis.wrxconfig.Model;
import com.teleofis.wrxconfig.model.SerialParameters;

public class SerialTransport {

	private final ManualResetEvent ctsState;
	
	private final ManualResetEvent received;
	
	private SerialPort serialPort;
	
	private String waitString = "";
	
	private String receivedString = "";

	public SerialTransport() {
		this.ctsState = new ManualResetEvent(true);
		this.received = new ManualResetEvent(false);
	}
	
	public boolean isOpen() {
		if ((serialPort != null) && (serialPort.isOpened())) {
			return true;
		}
		return false;
	}
	
	/**
	 * Close port
	 */
	public boolean close() {
		if ((serialPort != null) && (serialPort.isOpened())) {
			try {
				serialPort.closePort();
			} catch (SerialPortException e) {
				return false;
			}
			serialPort = null;
		}
		return true;
	}

	/**
	 * Open port
	 */
	public boolean open() {
		close();
		SerialParameters parameters = Model.INSTANCE.getModel().getSerialParameters();
		if(parameters == null) {
			return false;
		}
		serialPort = new SerialPort(parameters.getName());
		try {
			serialPort.openPort();
			serialPort.setParams(parameters.getBaudrate(), parameters.getDatabits(), 
					parameters.getStopbits(), parameters.getParity());
			
			serialPort.setEventsMask(SerialPort.MASK_RXCHAR | SerialPort.MASK_CTS);
			
			// Add SerialPortEventListener
			serialPort.addEventListener(new SerialPortReader());
		} catch (SerialPortException e) {
			return false;
		}
		return true;
	}
	
	/**
	 * 
	 * @author Pavel Gololobov
	 */
	class SerialPortReader implements SerialPortEventListener {
		public void serialEvent(SerialPortEvent event) {
			// If data is available
			if (event.isRXCHAR()) {
				try {
					int size = event.getEventValue();
					byte buffer[] = serialPort.readBytes(size);
					process(buffer);
				} catch (SerialPortException e) {
				}
			// CTS changed
			} else if (event.isCTS()) {
				if (event.getEventValue() == 1) {
					ctsState.set();
				} else {
					ctsState.reset();
				}
			}
		}
	}
	
	private void send(String data) {
		try {
			System.out.println("OUT: " + data);
			serialPort.writeString(data);
		} catch (SerialPortException e) {
			e.printStackTrace();
		}
	}
	
	private void send(byte[] data) {
		try {
			for(byte d : data) {
				try {
					ctsState.waitOne(5000, TimeUnit.MILLISECONDS);
				} catch (InterruptedException e) {
					return;
				}
				serialPort.writeByte(d);
			}
			System.out.println("OUT: binary data, Size: " + data.length);
		} catch (SerialPortException e) {
			e.printStackTrace();
		}
	}	
	
	private void process(byte[] buffer) {
		String str = new String(buffer);
		System.out.println("IN: " + str);
		receivedString += str;
		if(receivedString.indexOf(waitString) > -1) {
			received.set();
		}
	}

	private boolean waitString(int timeout) {
		boolean result = false;
		try {
			result = received.waitOne(timeout, TimeUnit.MILLISECONDS);
		} catch (InterruptedException e) {
			return false;
		}
		return result;
	}
	
	public boolean exchange(String out, String in, int timeout) {
		waitString = in;
		receivedString = "";
		received.reset();
		send(out);
		return waitString(timeout);
	}
	
	public boolean exchange(byte[] out, String in, int timeout) {
		waitString = in;
		receivedString = "";
		received.reset();
		send(out);
		return waitString(timeout);
	}

}
