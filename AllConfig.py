USBdic={}

class J17:
    
    pin2 = 0
    pin4 = 1
    pin6 = 2
    pin8 = 3
    pin10 = 4

class PCA9535J17:
    pin2 = 8
    pin4 = 9
    pin6 = 10
    pin8 = 11
    pin10 = 12
    
class J33:
    pin2 = 8
    pin4 = 9
    pin6 = 10
    pin8 = 11
    pin10 = 12

class PCA9535J33:
    pin2 = 0
    pin4 = 1
    pin6 = 2
    pin8 = 3
    pin10 = 4
    
class J34:
    pin2 = 13
    pin4 = 5
    pin6 = 14
    pin7 = 6
    pin9 = 15
    pin10 = 7

class PCA9535J34:
    pin2 = 5
    pin4 = 13
    pin6 = 6
    pin7 = 14
    pin9 = 7
    pin10 = 15

class J3:
    pin2 = 4
    pin5 = 5
    pin8 = 6
    pin10 = 7
class J2:
    pin2 = 0
    pin5 = 1
    pin8 = 2
    pin10 = 3  
    
class Track:
    YTrackID = ":0103020005F5"
    ZTrackID = ":0103020003F7"
    ATrainID = ":0103020002F8"
    BTrainID = ":0103020004F6"
    CheckSign = ":010310200001CB"
    Read901C = ":0103901C00014F"
    Origin = ":0106201E0003B8"
    YSpeed = ":01062014003293"##50%
    ZSpeed = ":01062014006461"##100%
    Move = ":0106201E0001BA"
    PositionStart = ":0110200200020400015F90D7"
    PositionCup2 = ":011020020002040001271E81"
    PositionIce = ":011020020002040000F7DAF6"
    PositionS1 = ":011020020002040000CF08F0"
    PositionS2 = ":011020020002040000ABC755"
    PositionS3 = ":0110200200020400008886B9"
    PositionS4 = ":01102002000204000065451D"
    PositionS5 = ":011020020002040000420481"
    PositionEnd = ":0110200200020400000000C7"
    ##YTrackA = ":011020020002040000B02CEB"##451mm
    ##YTrackA = ":011020020002040000AFC850"##450mm
    ##YTrackA = ":011020020002040000AF64B4"##449mm
    YTrackA = ":011020020002040000AE9C7D"##447mm
    ##YTrackA = ":011020020002040000ADD446"##445mm
    YTrackB = ":01102002000204000060E087"##248mm
    ##YTrackB = ":011020020002040000607CEB"##247mm
    YTrackEnd = ":011020020002040000E86C73"
    YTrackCup = ":0110200200020400000000C7"
    ZTrackUp = ":0110200200020400000000C7"
    ZTrackDown = ":0110200200020400005BCCA0"
    ZTrackPutCup = ":011020020002040000445C27"
    ZTrackWaitCup = ":0110200200020400003C8CFF"