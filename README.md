This is a bot you can either download the source code and run yourself with python localClient.py or sending a DM to Frc in osu!

The cool thing is this bot uses the v2 api so it will read your lazer plays and take them into account for recommendation + it will provide lazer pp values

Features:

!r > Will recommend you a map based on your top plays

!settings [banned_mods] [acc_preference] > change your preferences for the maps in !r

!settings acc_preference [95,98,100] > the bot will recommend you maps where getting your acc_preference will yield positive results, default is 98
!settings banned_mods > informative
!settings banned_mods [NM,HD,HR,HD+HR,HD+DT,HD+DT+HR] > toggle combinations of mods that you don't want to be sent by !r

Credits:
rosu-pp-py for performance calculation
ossapi for v2 api wrapper usage
