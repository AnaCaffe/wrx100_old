package com.teleofis.wrxconfig.model;

public class SerialParameters {
	
	private final String name;
	private final Integer baudrate;
	private final Integer databits;
	private final Integer stopbits;
	private final Integer parity;
	
	public SerialParameters(String name, int baudrate, int databits, int stopbits, int parity) {
		this.name = name;
		this.baudrate = baudrate;
		this.databits = databits;
		this.stopbits = stopbits;
		this.parity = parity;
	}
	
	/**
	 * Имя
	 * @return значение
	 */
	public String getName() {
		return name;
	}
	
	/**
	 * Скорость
	 * @return значение
	 */
	public int getBaudrate() {
		return baudrate.intValue();
	}
	
	/**
	 * Databits
	 * @return значение
	 */
	public int getDatabits() {
		return databits.intValue();
	}
	
	/**
	 * Stopbits
	 * @return значение
	 */
	public int getStopbits() {
		return stopbits.intValue();
	}
	
	/**
	 * Parity
	 * @return значение
	 */
	public int getParity() {
		return parity.intValue();
	}

	@Override
	public String toString() {
		return name;
	}
}
