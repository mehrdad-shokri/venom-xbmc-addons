# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
from resources.lib.comaddon import addon, dialog, window, listitem, xbmc, xbmcgui
from resources.lib.tmdb import cTMDb
from datetime import date, datetime

import unicodedata
import xbmcvfs
import time


# -----------------------
#     Cookies gestion
# ------------------------


class GestionCookie():
    PathCache = 'special://userdata/addon_data/plugin.video.vstream'
    
    def MakeListwithCookies(self,c):
        t = {}
        c = c.split(';')
        for i in c:
            j = i.split('=',1)
            if len(j) > 1:
                t[j[0]] = j[1]
            
        return t
        

    def DeleteCookie(self, Domain):
        Name = '/'.join([self.PathCache, 'cookie_%s.txt']) % (Domain)
        xbmcvfs.delete(Name)

    def SaveCookie(self, Domain, data):
        Name = '/'.join([self.PathCache, 'cookie_%s.txt']) % (Domain)

        # save it
        # file = open(Name, 'w')
        # file.write(data)
        # file.close()

        f = xbmcvfs.File(Name, 'w')
        f.write(data)
        f.close()

    def Readcookie(self, Domain):
        Name = '/'.join([self.PathCache, 'cookie_%s.txt']) % (Domain)

        # try:
        #     file = open(Name,'r')
        #     data = file.read()
        #     file.close()
        # except:
        #     return ''

        try:
            f = xbmcvfs.File(Name)
            data = f.read()
            f.close()
        except:
            return ''

        return data

    def AddCookies(self):
        cookies = self.Readcookie(self.__sHosterIdentifier)
        return 'Cookie=' + cookies
        
    def MixCookie(self,ancien_cookies, new_cookies):
        t1 = self.MakeListwithCookies(ancien_cookies)
        t2 = self.MakeListwithCookies(new_cookies)
        #Les nouveaux doivent ecraser les anciens
        for i in t2:
            t1[i] = t2[i]
                
        cookies = ''
        for c in t1:
            cookies = cookies + c + '=' + t1[c] + ';'
        cookies = cookies[:-1]
        return cookies

# -------------------------------
#     Configuration gestion
# -------------------------------

class cConfig():

    # def __init__(self):

        # import xbmcaddon
        # self.__oSettings = xbmcaddon.Addon(self.getPluginId())
        # self.__aLanguage = self.__oSettings.getLocalizedString
        # self.__setSetting = self.__oSettings.setSetting
        # self.__getSetting = self.__oSettings.getSetting
        # self.__oVersion = self.__oSettings.getAddonInfo('version')
        # self.__oId = self.__oSettings.getAddonInfo('id')
        # self.__oPath = self.__oSettings.getAddonInfo('path')
        # self.__oName = self.__oSettings.getAddonInfo('name')
        # self.__oCache = xbmc.translatePath(self.__oSettings.getAddonInfo('profile'))
        # self.__sRootArt = os.path.join(self.__oPath, 'resources' , 'art', '')
        # self.__sIcon = os.path.join(self.__oPath,'resources', 'art','icon.png')
        # self.__sFanart = os.path.join(self.__oPath,'resources','art','fanart.jpg')
        # self.__sFileFav = os.path.join(self.__oCache,'favourite.db').decode('utf-8')
        # self.__sFileDB = os.path.join(self.__oCache,'vstream.db').decode('utf-8')
        # self.__sFileCache = os.path.join(self.__oCache,'video_cache.db').decode('utf-8')

    def isDharma(self):
        return self.__bIsDharma

    def getSettingCache(self):
        return False

    def getAddonPath(self):
        return False

    def getRootArt(self):
        return False

    def getFileFav(self):
        return False

    def getFileDB(self):
        return False

    def getFileCache(self):
        return False


def WindowsBoxes(sTitle, sFileName, num, year=''):

    ADDON = addon()
    DIALOG = dialog()

    # Presence de l'addon ExtendedInfo?
    try:
        if (addon('script.extendedinfo') and ADDON.getSetting('extendedinfo-view') == 'true'):
            if num == '2':
                DIALOG.VSinfo('Lancement de ExtendInfo')
                xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo, info=extendedtvinfo, name=%s)' % sFileName)
                return
            elif num == '1':
                DIALOG.VSinfo('Lancement de ExtendInfo')
                xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo, info=extendedinfo, name=%s)' % sFileName)
                return
    except:
        pass
    

    # Sinon on gere par vStream via la lib TMDB
    if num == '1':
        try:
            grab = cTMDb()
            meta = grab.get_meta('movie', sFileName, '', xbmc.getInfoLabel('ListItem.Property(TmdbId)'))
        except:
            DIALOG.VSok("Veuillez vider le cache des métadonnées Paramètre - outils - 'vider le cache de vStream'")
            pass
    elif num == '2':
        try:
            grab = cTMDb()
            meta = grab.get_meta('tvshow', sFileName, '', xbmc.getInfoLabel('ListItem.Property(TmdbId)'))
        except:
            DIALOG.VSok("Veuillez vider le cache des métadonnées Paramètre - outils - 'vider le cache de vStream'")
            pass
        

    # si rien ne marche
    if (not meta['imdb_id'] and not ['tmdb_id'] and not ['tvdb_id']):
        # dialog par defaut
        # xbmc.executebuiltin('Action(Info)')
        # fenetre d'erreur
        DIALOG.VSinfo(ADDON.VSlang(30204))
        return

    # convertion de la date au format JJ/MM/AAAA
    if 'premiered' in meta and meta['premiered']:
        releaseDate = datetime(*(time.strptime(meta['premiered'], '%Y-%m-%d')[0:6]))
        meta['releaseDate'] = releaseDate.strftime('%d/%m/%Y')

    # convertion de la durée en secondes -> heure:minutes
    if 'duration' in meta and meta['duration']:
        duration = meta['duration']/60  # En minutes
        durationH = duration/60 # Nombre d'heures
        meta['durationH'] = durationH
        meta['durationM'] = '{:02d}'.format(duration - 60*durationH)
    else:
        meta['durationH'] = 0
        meta['durationM'] = 0

    # affichage du dialog perso
    class XMLDialog(xbmcgui.WindowXMLDialog):

        ADDON = addon()
        """
        Dialog class that asks user about rating of movie.
        """
        def __init__(self, *args, **kwargs):
            xbmcgui.WindowXMLDialog.__init__(self)
            pass

        # def message(self, message):
            # """
            # Shows xbmc dialog with OK and message.
            # """
            # dialog = xbmcgui.Dialog()
            # dialog.ok(' My message title', message)
            # self.close()

        def onInit(self):
            # par default le resumer#
            color = ADDON.getSetting('deco_color')
            window(10000).setProperty('color', color)
            self.poster = 'https://image.tmdb.org/t/p/%s' % self.ADDON.getSetting('poster_tmdb')
            self.none_poster = 'https://eu.ui-avatars.com/api/?background=000&size=512&name=%s&color=FFF&font-size=0.33'

            #self.getControl(50).setVisible(False)
            #self.getControl(90).setVisible(False)
            #self.getControl(5200).setVisible(False)
            #self.getControl(52100).setVisible(False)
            #self.getControl(52200).setVisible(False)
            # synopsis_first
            self.setFocusId(9000)

            # self.getControl(50).reset()
            listitems = []
            listitems2 = []
            cast = []
            crew = []
            
            data = eval(str(meta['credits']).decode('utf-8'))

            try:
                for i in data['cast']:
                    slabel = i['name']
                    slabel2 = i['character']
                    if i['profile_path']:
                        sicon = self.poster+str(i['profile_path'])
                    else :
                        sicon = self.none_poster % slabel
                    sid = i['id']
                    listitem_ = listitem(label=slabel, label2=slabel2, iconImage=sicon)
                    listitem_.setProperty('id', str(sid))
                    listitems.append(listitem_)
                    cast.append(slabel.encode('ascii', 'ignore'))
                self.getControl(50).addItems(listitems)
            except:
                pass
            
            try:
                for i in data['crew']:
                    slabel = i['name']
                    slabel2 = i['job']
                    if i['profile_path']:
                        sicon = self.poster+str(i['profile_path'])
                    else :
                        sicon = self.none_poster % slabel
                    sid = i['id']
                    listitem_ = listitem(label=slabel, label2=slabel2, iconImage=sicon)
                    listitem_.setProperty('id', str(sid))
                    listitems2.append(listitem_)
                    crew.append(slabel.encode('ascii', 'ignore'))
                self.getControl(5200).addItems(listitems2)
            except:
                pass

            # try:
            #     for slabel, slabel2, sicon, sid in meta['cast']:
            #         listitem_ = listitem(label=slabel, label2=slabel2, iconImage=sicon)
            #         listitem_.setProperty('id', str(sid))
            #         listitems.append(listitem_)
            #         cast.append(slabel.encode('ascii', 'ignore'))
            #     self.getControl(50).addItems(listitems)
            #     #window(10000).setProperty('ListItem.casting', str(cast))
            # except:
            #     pass
            
            # title
            # self.getControl(1).setLabel(meta['title'])
            meta['title'] = sTitle

            # self.getControl(49).setVisible(True)
            # self.getControl(2).setImage(meta['cover_url'])
            # self.getControl(3).setLabel(meta['rating'])

            for e in meta:
                property = 'ListItem.%s' % (e)
                if isinstance(meta[e], unicode):
                    window(10000).setProperty(property, meta[e].encode('utf-8'))
                else:
                    window(10000).setProperty(property, str(meta[e]))

        def credit(self, meta='', control=''):
            #self.getControl(control).reset()
            listitems = []
            
            if not meta:
                meta = [{u'id': 0, u'title': u'Aucune information', u'poster_path': u'', u'vote_average':0}]

            try:
                for i in meta:
                    try:
                        sTitle = unicodedata.normalize('NFKD', i['title']).encode('ascii', 'ignore')
                    except:
                        sTitle = 'Aucune information'
                        
                    if i['poster_path']:
                        sThumbnail = self.poster+str(i['poster_path'])
                    else :
                        sThumbnail = self.none_poster % sTitle
                    
                    sId = i['id']

                    listitem_ = listitem(label=sTitle, iconImage=sThumbnail)
                    try:
                        listitem_.setInfo('video', {'rating': i['vote_average'].encode('utf-8') })
                    except:
                        listitem_.setInfo('video', {'rating': str(i['vote_average'])})

                    listitems.append(listitem_)
                self.getControl(control).addItems(listitems)

            except:
                pass
            
            #self.getControl(52100).setVisible(False)
            #self.getControl(52200).setVisible(True)
            #self.setFocusId(5205)
            # self.setFocus(self.getControl(5200))

        def onClick(self, controlId):
            #print(controlId)
            if controlId == 11:
                from resources.lib.ba import cShowBA
                cBA = cShowBA()
                cBA.SetSearch(sFileName)
                cBA.SearchBA(True)
                #self.close()
                return
            elif controlId == 30:
                self.close()
                return
            elif controlId == 50 or controlId == 5200 :
                # print(self.getControl(50).ListItem.Property('id'))
                item = self.getControl(controlId).getSelectedItem()
                sid = item.getProperty('id')
                

                grab = cTMDb()
                sUrl = 'person/' + str(sid)
                
                
                try:
                    meta = grab.getUrl(sUrl, '', "append_to_response=movie_credits,tv_credits")
                    meta_credits = meta['movie_credits']['cast']
                    self.credit(meta_credits, 5215)
                    
         
                    try:
                        sTitle = unicodedata.normalize('NFKD', meta['name']).encode('ascii', 'ignore')
                    except:
                        sTitle = 'Aucune information'
                    
                    if not meta['deathday']:
                        today = date.today()
                        try:
                            birthday = datetime(*(time.strptime(meta['birthday'], '%Y-%m-%d')[0:6]))
                            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
                            age = '%s Ans' % age
                        except:
                            age = ''
                    else:
                        age = meta['deathday']
                        
                  
                    window(10000).setProperty('Person_name', sTitle)
                    window(10000).setProperty('Person_birthday', meta['birthday'])
                    window(10000).setProperty('Person_place_of_birth', meta['place_of_birth'])
                    window(10000).setProperty('Person_deathday', str(age))
                    window(10000).setProperty('Person_biography', meta['biography']) 
                    self.setFocusId(9000)                   
       
                except:
                    return
                # self.getControl(50).setVisible(True)
                self.setProperty('vstream_menu', 'Person')
            # click sur similaire
            elif controlId == 9:
                # print(self.getControl(9000).ListItem.tmdb_id)
                sid = window(10000).getProperty('ListItem.tmdb_id')

                grab = cTMDb()
                sUrl_simil = 'movie/%s/similar' % str(sid)
                sUrl_recom = 'movie/%s/recommendations' % str(sid)
                
                try:
                    meta = grab.getUrl(sUrl_simil)
                    meta = meta['results']
                    self.credit(meta, 5205)
                except:
                    pass
                try:
                    meta = grab.getUrl(sUrl_recom)
                    meta = meta['results']
                    self.credit(meta, 5210)
                except:
                    return

            elif controlId == 5215 or controlId == 5205 or controlId == 5210:
                # click pour recherche
                import sys
                from resources.lib.util import cUtil
                item = self.getControl(controlId).getSelectedItem()
                sTitle = item.getLabel()

                try:
                    sTitle = sTitle.encode('utf-8')
                    sTitle = cUtil().CleanName(sTitle)
                except:
                    return

                sTest = '%s?site=globalSearch&searchtext=%s&sCat=1' % (sys.argv[0], sTitle)
                xbmc.executebuiltin('XBMC.Container.Update(%s)' % sTest)
                self.close()
                return
            # elif controlId == 2:
            #     print("paseeeee")
            #     xbmc.executebuiltin('Dialog.Close(all, force)')
            #     xbmc.executebuiltin('ActivateWindow(12005)')
            #     return

        def onFocus(self, controlId):
            self.controlId = controlId
            #fullscreen end return focus menu
            if controlId == 40:
                while xbmc.Player().isPlaying():
                    xbmc.sleep(500)
                    if not xbmc.Player().isPlaying():
                        self.setFocusId(9000)
                    
            #if controlId != 5200:
                # self.getControl(5500).reset()
            #  self.getControl(5200).setVisible(False)
            # if controlId == 50:
                # item = self.getControl(50).getSelectedItem()
                # sid = item.getProperty('id')

        def _close_dialog(self):
            self.close()

        def onAction(self, action):
            if action.getId() in (104, 105, 1, 2):
                return

            if action.getId() in (9, 10, 11, 30, 92, 216, 247, 257, 275, 61467, 61448):
                self.close()

    path = 'special://home/addons/plugin.video.vstream'
    # self.__oPath.decode('utf-8')
    wd = XMLDialog('DialogInfo4.xml', path, 'default', '720p')
    wd.doModal()
    del wd
