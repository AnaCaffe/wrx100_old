package com.teleofis.wrxconfig.telit;

import com.teleofis.utils.FileStream;
import com.teleofis.wrxconfig.transport.SerialTransport;

public class TelitLoader {
	
	private final SerialTransport transport;

	public TelitLoader(SerialTransport transport) {
		this.transport = transport;
	}

	private boolean checkConnection() {
		boolean result = transport.exchange("AT\r", "OK", 3000);
		return result;
	}
	
	private boolean deleteFile(String file) {
		boolean result = transport.exchange("AT#DSCRIPT=\"" + file + "\"\r", "OK", 3000);
		return result;
	}
	
	private boolean writeFile(String path, String file) {
		boolean result = false;
		byte[] data = FileStream.read(path + file);

		result = transport.exchange("AT#WSCRIPT=\"" + file + "\"," + Integer.toString(data.length) + "\r", ">>>", 3000);
		if(result) {
			result = transport.exchange(data, "OK", 3000);
		}
		
		return result;
	}
	
	@SuppressWarnings("unused")
	private boolean listFiles() {
		boolean result = transport.exchange("AT#LSCRIPT\r", "OK", 3000);
		return result;
	}
	
	private boolean enableFile(String file) {
		boolean result = transport.exchange("AT#ESCRIPT=\"" + file + "\"\r", "OK", 3000);
		return result;
	}
	
	private boolean executeFile() {
		boolean result = transport.exchange("AT#EXECSCR\r", "OK", 3000);
		return result;
	}
	
	public boolean upload(String path, String filter) {
		boolean result = false;
		String[] files = FileStream.getFilesList(path, filter);
		if(files.length == 0) {
			return false;
		}
		result = checkConnection();
		if(result) {
			for(String file : files) {
				deleteFile(file);
				result = writeFile(path, file);
			}
		}
		return result;
	}
	
	public boolean start(String name) {
		boolean result = enableFile(name);
		if(result) {
			result = executeFile();
		}
		return result;
	}
}
