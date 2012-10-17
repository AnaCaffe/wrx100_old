package com.teleofis.wrxconfig.transport;

public interface ITransport {
	boolean close();
	boolean open();
	void send(String data);
	void send(byte[] data);
}
