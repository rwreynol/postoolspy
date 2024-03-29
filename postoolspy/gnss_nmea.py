import re

class nmea_parser:
    '''
    nmea parser
    '''

    def checksum(self,string):
        msg = re.findall(r'\$(.*?)\*',string)[0]
        csum = 0
        for s in msg:
            csum = csum ^ ord(s)
        return '%X' % csum

    def parse(self,string):
        '''
        parse nmea string
        '''
        try:
            msgid = re.findall(r'\$(.*?),',string)[0]
            chksm = re.findall(r'\*(.*?)\s',string)[0]
            calc_chksm = self.checksum(string)
            #print(msgid,chksm,calc_chksm)

            if chksm != calc_chksm:
                print('Checksums dont match')
                return nmea_result()  
            elif bool(re.search(r'G[NPL]GGA',msgid)):# parse gga string
                return self._parse_gga(string)
            elif msgid == 'IMU':# parse gga string
                return self._parse_imu(string)
            else:
                print('Unknown NMEA identifier')
                return nmea_result()
            
        except Exception as e:
            print(str(e))
            return nmea_result()
        
    def _parse_imu(self,string):
        info = re.split(r',',string.strip())
        yaw = float(info[1])
        pitch = float(info[2])
        roll = float(info[3][0:-3])
        return nmea_result(identity='IMU',yaw=yaw,pitch=pitch,roll=roll)

    def _parse_gga(self,string):
        '''
        parse gga
        '''
        info = re.split(r',',string.strip())
        t = self._parse_time(info[1])
        lat = self._parse_lat(info[2],info[3])
        lon = self._parse_lon(info[4],info[5])
        quality = float(info[6])
        numSV = float(info[7])
        alt = float(info[9])

        return nmea_result(identity='GGA',time=t,lat=lat,lon=lon,quality=quality,numSV=numSV,alt=alt)

    def _parse_time(self,str_time):
        '''
        parse time
        '''
        t = re.split(r'\.',str_time)
        t_gps = float(t[0][0:2])*3600 + float(t[0][2:4]) * 60 + float(t[0][4:]) + .001*float(t[1])
        return t_gps
    
    def _parse_lat(self,str_lat,dir_lat):
        '''
        parse latitude
        '''
        l = re.split(r'\.',str_lat)
        lat = float(l[0][0:-2]) + float(l[0][-2:] + '.' + l[1])/60.0

        if dir_lat == 'S': lat *= -1
        return lat
    
    def _parse_lon(self,str_lon,dir_lon):
        '''
        parse longitude
        '''
        l = re.split(r'\.',str_lon)
        lon = float(l[0][0:-2]) + float(l[0][-2:] + '.' + l[1])/60.0

        if dir_lon == 'W': lon *= -1
        return lon

    def _parse_gga_slam(self,string):
        '''
        pars gga slam
        '''
        pass

class nmea_result(object):
    '''
    parsed nmea string results
    '''

    msg_id = 'none'

    def __init__(self,**kwargs):
        '''
        constructor
        '''
        self.__dict__.update(kwargs)

    def __str__(self):
        '''
        override object string formation
        '''
        return str(self.__dict__)
