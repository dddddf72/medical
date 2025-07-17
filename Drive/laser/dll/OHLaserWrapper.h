/***************************************************************************
**                                                                        **
**  OHLaserWrapper, an easy to use,										  **
**  a cross platform interface for interacting with USB Ports             **
**  Copyright (C) 2011-2016 Emanuel Eichhammer                            **
****************************************************************************
**           Author: Marcos.wang  <Marcos.wang@oceanhood.com>             **
**  Website/Contact: http://www.oceanhood.com/                            **
**             Date: 17.10.26                                             **
**          Version: 2.1.0-beta                                           **
****************************************************************************/

#ifndef OHLASERWRAPPER_H
#define OHLASERWRAPPER_H

#ifdef __cplusplus
extern "C"
{
#endif

/*!
*defines the possible bytesizes for the laser error code.
*/
#define NO_DEVICE_ERROR					2
#define DATA_SWAP_ERROR					3
#define MODULE_NO_SUPPORT_ERROR			4
#define LASER_HANDSHAKE_ERROR			5
#define LASER_NO_MODULE_ERROR			10

/*!
* Enumeration defines the possible bytesizes for the laser status.
*/
typedef enum
{
	LASER_NORMAL,
	LASER_INTERLOCK_UNENABLE,
	LASER_ENABLE_UNENABLE,
	LASER_FAN_FAIL,
	LASER_WAIT_TEC,
	LASER_EX_CONTROL,
	LASER_SOFT_MODE,
	LASER_MAX_VOLTAGE_PER10,
	LASER_MAX_VOLTAGE_PER20,
	LASER_MAX_VOLTAGE_PER30,
	LASER_MAX_VOLTAGE_PER40,
	LASER_MAX_VOLTAGE_PER50,
	LASER_MAX_VOLTAGE_PER60,
	LASER_MAX_VOLTAGE_PER80,
	LASER_MAX_VOLTAGE_PER100,
	LASER_RESERVED,
	LASER_UNKNOW
}LASER_STATUS;

/*!
* Enumeration defines the possible bytesizes for the laser factory information.
*/
typedef struct
{
	char ProductModel[16];
	char ProductMiddleWave[8];
	char ProductSerialNumber[16];	
	char ProductDate[16];
	char ProductMinPower[4];
	char ProductMaxPower[4];
	char ProductPCBVersion[16];
	char ProductHexVersion[8];
	char ProductCalibration[2];
}FACTORY_INFORMATION;

/* Function prototypes */

/*!
* Function: enumerateDevices
* Description:enumerate all the usb port and the ports don't open.
* Input: 
* Output:
* Return:number of usb devices
* Other: 
*/
int enumerateDevices(void);

/*!
* Function: openDevice
* Description:Opens the USB , the port is set and the port isn't already open.
* Input: \param index:number of device that you want to open
* Output: 
* Return:0:open fail,1:open success, 2:not soft mode 
* Other:
*/
int openDevice(int index);

/*!
* Function: closeDevice
* Description:Close the USB,the port is setted and the port is already opened.
* Input: \param index:number of device that you want to close
* Output:
* Return:1:close success, 0:colse fail 2:switch posion not on 0
* Other:
*/
int closeDevice(int index);

/*!
* Function: handShakeLaser
* Description:hand shake with laser.
* Input: \param index:number of device that opend
* Output:
* Return:1:hand shake success, 0:hand shake fail
* Other:
*/
int handShakeLaser(int index);

/*!
* Function: setLaserEnable
* Description:Enable laser.
* Input: \param enable true:set laser enable false:set laser disable
*		 \param index:number of device that opend
* Output:
* Return:1:Enable success, 0:Enable fail
* Other:
*/
int setLaserEnable(int index, bool enable);

/*!
* Function: getLaserStatus
* Description:Get laser status.
* Input:\param index:number of device that opend
* Output: 0:normal,1:interlock unenable,2:enable unenable,
* 3:fan error,4:wait tec,5:extern control
* Return:1:Get laser status success, 0:Get laser status fail
* Other:
*/
int getLaserStatus(int index, unsigned char* status);

/*!
* Function: setLaserVoltage
* Description:Set laser voltage.
* Input:\param voltage:set voltage value
*		\param index:number of device that opend
* Output:
* Return:1:set laser voltage success, 0:set laser voltage fail
* Other:
*/
int setLaserVoltage(int index, double voltage);

/*!
* Function: getLaserVoltage
* Description:get laser voltage.
* Input:\param voltage:get voltage value
*		\param index:number of device that opend
* Output:
* Return:1:get laser voltage success, 0:get laser voltage fail
* Other:
*/
int getLaserVoltage(int index, double* voltage);

/*!
* Function: setLaserPower
* Description:Set laser power.
* Input:\param power:set power value
*		\param index:number of device that opend
* Output:
* Return:1:set laser power success, 0:set laser power fail
* Other:
*/
int setLaserPower(int index, double power);

/*!
* Function: getLaserPower
* Description:get laser power.
* Input:\param power:get power value
*		\param index:number of device that opend
* Output:
* Return:1:get laser power success, 0:get laser power fail
* Other:
*/
int getLaserPower(int index, double* power);

/*!
* Function: setLaserVoltageCoef
* Description:set laser voltage coefficient.
* Input:\param a,b,c,d,e,f,g,h:set voltage coefficient value
*		\param index:number of device that opend
* Output:
* Return:1:set laser voltage coefficient success, 0:set laser voltage coefficient fail
* Other:
*/
int setLaserVoltageCoef(int index, double a, double b, double c, double d, double e, double f, double g, double h );

/*!
* Function: getLaserVoltageCoef
* Description:get laser voltage coefficient.
* Input: \param index:number of device that opend
* Output:\param a,b,c,d,e,f,g,h:get voltage coefficient value
* Return:1:get laser voltage coefficient success, 0:get laser voltage coefficient fail
* Other:
*/
int getLaserVoltageCoef(int index, double* a, double* b, double* c, double* d, double* e, double* f, double* g, double* h);

/*!
* Function: setLaserPowerCoef
* Description:set laser power coefficient.
* Input:\param a,b,c,d,e,f,g,h:set power coefficient value
*		\param index:number of device that opend
* Output:
* Return:1:set laser power coefficient success, 0:set laser power coefficient fail
* Other:
*/
int setLaserPowerCoef(int index, double a, double b, double c, double d, double e, double f, double g, double h);

/*!
* Function: getLaserPowerCoef
* Description:get laser power coefficient.
* Input: \param index:number of device that opend
* Output:\param a,b,c,d,e,f,g,h:get power coefficient value
* Return:1:get laser power coefficient success, 0:get laser power coefficient fail
* Other:
*/
int getLaserPowerCoef(int index, double* a, double* b, double* c, double* d, double* e, double* f, double* g, double* h);

/*!
* Function: getLaserTECTemperature
* Description:get TEC temperature.
* Input: \param index:number of device that opend
* Output:\param temp:get TEC temperature value
* Return:1:get TEC temperature success, 0:get TEC temperature fail
* Other:
*/
int getLaserTECTemperature(int index, double* temp);

/*!
* Function: getLaserBoxTemperature
* Description:get box temperature.
* Input: \param index:number of device that opend
* Output:\param temp:get box temperature value
* Return:1:get box temperature success, 0:get box temperature fail
* Other:
*/
int getLaserBoxTemperature(int index, double* temp);

/*!
* Function: getLaserSwitchPosition
* Description:get the dial switch location number.
* Input: \param index:number of device that opend
* Output:\param position:get the dial switch location number
* 0:soft mode  
* 1:hardware mode ,maximum voltage of %10,
* 2:hardware mode ,maximum voltage of %20,3:hardware mode ,maximum voltage of %30,
* 4:hardware mode ,maximum voltage of %40,5:hardware mode ,maximum voltage of %50,
* 6:hardware mode ,maximum voltage of %60,7:hardware mode ,maximum voltage of %80,
* 8:hardware mode ,maximum voltage of %100,9:hardware mode ,Reserved
* Return:1:get the dial switch location number success, 0:get the dial switch location number fail
* Other:
*/
int getLaserSwitchPosition(int index, unsigned char* position);

/*!
* Function: setLaserFactoryInfo
* Description:set the factory information,see detail,struct FACTORY_INFORMATION.
* Input: \param index:number of device that opend
* Output:\param info:set the factory information
* Return:1:set the factory information success, 0:set the factory information fail
* Other:
*/
int setLaserFactoryInfo(int index, FACTORY_INFORMATION* info);

/*!
* Function: getLaserFactoryInfo
* Description:get the factory information,see detail,struct FACTORY_INFORMATION.
* Input: \param index:number of device that opend
* Output:\param info:get the factory information
* Return:1:get the factory information success, 0:get the factory information fail
* Other:
*/
int getLaserFactoryInfo(int index, FACTORY_INFORMATION* info);

/*!
* Function: getLaserModule
* Description:get the factory information of module,see detail,struct FACTORY_INFORMATION.
* Input: \param index:number of device that opend
* Output:\param module:get the factory information of module
* Return:1:get the factory information of module success, 0:get the factory information fail of module
* Other:
*/
int getLaserModule(int index, char* module);

/*!
* Function: getLaserSerialNumber
* Description:get the factory information of serial number,see detail,struct FACTORY_INFORMATION.
* Input: \param index:number of device that opend
* Output:\param module:get the factory information of serial number
* Return:1:get the factory information of serial number success, 0:get the factory information fail of serial number
* Other:
*/
int getLaserSerialNumber(int index, char* serialnumber);

/*!
* Function: getLaserWavelength
* Description:get the factory information of middle wave,see detail,struct FACTORY_INFORMATION.
* Input: \param index:number of device that opend
* Output:\param module:get the factory information of wavelength
* Return:1:get the factory information of wavelength success, 0:get the factory information fail of wavelength
* Other:
*/
int getLaserWavelength(int index, double* wavelength);

/*!
* Function: getLaserPowerRange
* Description:get the factory information of min power,see detail,struct FACTORY_INFORMATION.
* Input: \param index:number of device that opend
* Output:\param module:get the factory information of min power,max power
* Return:1:get the factory information of  power success, 0:get the factory information fail of  power
* Other:
*/
int getLaserPowerRange(int index, int* minpower, int* maxpower);

#ifdef __cplusplus
}
#endif

#endif//OHLASERWRAPPER_H


