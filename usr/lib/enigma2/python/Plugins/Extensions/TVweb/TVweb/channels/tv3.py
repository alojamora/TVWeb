# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para TV3
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import re
import sys
import os
import traceback
import urllib2

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools


__channel__ = "tv3"
__category__ = "S"
__type__ = "generic"
__title__ = "TV3"
__language__ = "ES"
__creationdate__ = "20120212"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[tv3.py] mainlist")
    
    itemlist = []
    
    itemlist.append( Item(channel=__channel__, title="Alta definicio", action="hdvideolist", url = "http://www.tv3.cat/pprogrames/hd/mhdSeccio.jsp") )
    itemlist.append( Item(channel=__channel__, title="Series", action="loadsection" , extra = "TSERIES|") )
    itemlist.append( Item(channel=__channel__, title="Actualitat", action="loadsection" , extra = "TACTUALITA|") )
    itemlist.append( Item(channel=__channel__, title="Esports", action="loadsection", extra = "TESPORTS|" ) )
    itemlist.append( Item(channel=__channel__, title="Cuina", action="loadsection" , extra = "TCUINA|") )    
    itemlist.append( Item(channel=__channel__, title="Entreteniment", action="loadsection" , extra= "TENTRETENI|" ) )
    itemlist.append( Item(channel=__channel__, title="Divulgacio", action="loadsection" , extra= "TDIVULGACI|" ) )
    itemlist.append( Item(channel=__channel__, title="Juvenil", action="loadsection" , extra= "TJUVENIL|" ) )
    itemlist.append( Item(channel=__channel__, title="Infantil", action="loadsection" , extra= "TINFANTIL|" ) )
    itemlist.append( Item(channel=__channel__, title="Musica", action="loadsection" , extra= "TMUSICA|" ) )
    itemlist.append( Item(channel=__channel__, title="Gent TVC", action="loadsection" , extra= "TGENTTVC|" ) )
    itemlist.append( Item(channel=__channel__, title="Buscar", action="search") )
    
    
    return itemlist



def loadsection(item):
    try:
        logger.info("[tv3.py] loadsection")
        
        itemlist = []
        
        categoria, post = item.extra.split('|')
        if len(post) == 0:
            url = "http://www.tv3.cat/searcher/tvc/searchingVideos.jsp?acat=" + categoria
            data = scrapertools.cachePage(url)
        else:
            url = item.url
            data = scrapertools.cachePage(url,post)
            
        #<input type="hidden" name="endDate" value="01/02/2009"/>
        patron = '<input type="hidden" name="endDate" value="([^"]+)"'
        fecha = re.compile(patron,re.DOTALL).findall(data)
	
        # --------------------------------------------------------
        # Extrae los videos
        # --------------------------------------------------------
        patron = '<li>.*?<div class="img_p_txt_mes_a">(.*?)</li>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        if len(matches) > 0:
            for chapter in matches:
                try:
                    patron = '<img src="([^"]+)"'
                    matches = re.compile(patron,re.DOTALL).findall(chapter)
                    scrapedthumbnail = matches[0]
                    
                    patron = '<span class="avant">([^<]+)</span>'                
                    matches = re.compile(patron,re.DOTALL).findall(chapter)
                    scrapedtitle = matches[0]
                    
                    patron= '<a href="([^"]+)">([^<]+)</a>'                
                    matches = re.compile(patron,re.DOTALL).findall(chapter)
                    scrapedurl = "http://www.tv3.cat%s" % matches[0][0]
                    scrapedtitle = scrapedtitle + " - \"" + matches[0][1] + "\""
                    
                    patron= '<p>([^<]+)<'                
                    matches = re.compile(patron,re.DOTALL).findall(chapter)
                    scrapedplot = matches[0]
                    
                    # Añade al listado de XBMC
                    itemlist.append(
                        Item(channel=item.channel,
                             action = 'links',
                             title = str(scrapedtitle).replace("&quot;", "'"),
                             url = scrapedurl,
                             thumbnail = scrapedthumbnail,
                             plot = scrapedplot
                        )
                    ) 
                except:
                    import sys
                    for line in sys.exc_info():
                        logger.error( "%s" % line )  
                        
            
        # Extrae el paginador
        patron = '<li class="lastpag">.*?send\(\'frmSearcher\',.*?(\d+)\)".*?</li>'
        numeros = re.compile(patron,re.DOTALL).findall(data)
        
        if len(numeros)>0 :
            post = 'hiPortal=tvc&hiSearchEngine=lucene&hiAdvanced=1&hiSearchIn=0&maxRowsDisplay=25&hiStartValue=%s&startDate=&endDate=%s&textBusca=&hiCategory=VID&acat=%s&hiTarget=searchingVideos.jsp' % ( numeros[0], fecha[0], categoria )
    
            urlsiguiente = "http://www.tv3.cat/searcher/Search"
            extrasiguiente = categoria + "|" + post 
            
            # Añade al listado de XBMC
            itemlist.append(
                Item(channel=item.channel,
                     action = 'loadsection',
                     title = 'Siguiente',
                     url = urlsiguiente,
                     thumbnail = '',
                     plot = "",
                     extra = extrasiguiente
                )
            )  
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
		
    return itemlist
   
def search(item,texto, categoria="*"):
    item.extra= texto + "|1"
    
    return dosearch(item)
    
def dosearch(item):
        
    texto, start = item.extra.split('|')
    
    itemlist = []
    post = 'hiPortal=tvc'
    post = post + '&hiSearchEngine=lucene'
    post = post + '&hiAdvanced=1'
    post = post + '&hiSearchIn=0'
    post = post + '&maxRowsDisplay=50'
    post = post + '&hiStartValue=' + start
    post = post + '&hiTarget=searching.jsp'
    post = post + '&hiCategory=VID'
    post = post + '&textBusca=' + texto
    
    url = "http://www.tv3.cat/searcher/Search"
    data = scrapertools.cachePage(url,post)
    
    #resultado busqueda
    patron = '<div class="resultatcercador">.*?</body>'            
    matches = re.compile(patron,re.DOTALL).findall(data)
    data = matches[0]
    
    patron = '<li>.*?<p class="topitem">.*?</ul>.*?</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches) > 0:
        for chapter in matches:
            try:
                patron = '<img src="([^"]+)"'
                matches = re.compile(patron,re.DOTALL).findall(chapter)
                scrapedthumbnail = matches[0]
                
                patron = '<span class="avant">([^<]+)</span>'                
                matches = re.compile(patron,re.DOTALL).findall(chapter)
                scrapedtitle = matches[0]
                
                patron= '<h2>.*?<a.*?href="([^"]+)">([^<]+)</a>'                
                matches = re.compile(patron,re.DOTALL).findall(chapter)
                scrapedurl = "http://www.tv3.cat%s" % matches[0][0]
                scrapedtitle = scrapedtitle + " - \"" + matches[0][1] + "\""
                
                patron= '<p>([^<]+)<'                
                matches = re.compile(patron,re.DOTALL).findall(chapter)
                scrapedplot = matches[0]
                
                # Añade al listado de XBMC
                itemlist.append(
                    Item(channel=item.channel,
                         action = 'links',
                         title = str(scrapedtitle).replace("&quot;", "'"),
                         url = scrapedurl,
                         thumbnail = scrapedthumbnail,
                         plot = scrapedplot
                    )
                ) 
            except:
                import sys
                for line in sys.exc_info():
                    logger.error( "%s" % line ) 
        try:          
            # Extrae el paginador
            patron = 'sendGet\(\'frmSeaPag\',[^\)]+\)" class="fletxes" title="[^.]+. se[^"]+">'
            matches = re.compile(patron,re.DOTALL).findall(data)
            data = matches [0]
            
            patron = '\'frmSeaPag\',.*?(\d+)\)"'
            numeros = re.compile(patron,re.DOTALL).findall(data)
            
            if len(numeros)>0 :
                extrasiguiente = texto + "|" + numeros[0] 
                
                # Añade al listado de XBMC
                itemlist.append(
                    Item(channel=item.channel,
                         action = 'dosearch',
                         title = 'Siguiente',
                         extra = extrasiguiente
                    )
                ) 
        except:
            import sys
            for line in sys.exc_info():
                logger.error( "%s" % line ) 
    
    return itemlist

def hdvideolist(item):
    logger.info("[tv3.py] hdvideolist")
    itemlist = []
    try:
        # --------------------------------------------------------
        # Descarga la pagina
        # --------------------------------------------------------
        data = scrapertools.cachePage(item.url)
        data = data.replace("\\\"","")
        
        # --------------------------------------------------------
        # Extrae los programas
        # --------------------------------------------------------
        #addItemToVideoList( 0, 
        # 0 "Ana Maria Matute: \"making of\"", 
        # 1 "1427429", 
        # 2 "http://hd.tv3.cat/720/SAVIS_INTERNET_MATUTE_MAKIN_TV3H264_720.mp4" , 
        # 3 "http://hd.tv3.cat/1080/SAVIS_INTERNET_MATUTE_MAKIN_TV3H264_1080.mp4" , 
        # 4 "http://www.tv3.cat/multimedia/jpg/5/4/1253613702545.jpg", 
        # 5 "http://www.tv3.cat/multimedia/jpg/5/4/1253613702545.jpg", 
        # 6 "http://www.tv3.cat/multimedia/jpg/5/4/1253613702545.jpg", 
        # 7 "\"Making of\" del cap�tol de Savis on s'entrevista a Ana Maria Matute. Enregistrat al Castell Santa Florentina." , 
        # 8 "0:58" , 
        # 9 " mgb.", 
        #10 " mgb.", 
        #11 "Savis", "http://www.tv3.cat/multimedia/gif/0/5/1250763975650.gif", "http://www.tv3.cat/multimedia/gif/2/9/1250763944192.gif", "Documental" , "http://www.tv3.cat/programa/11605" , "http://www.tv3.cat/multimedia/jpg/5/0/1253613661005.jpg" , "Web de programa", "20091019");
        
        
        #addItemToVideoList( 2, "El búnquer", "871599", "http://hd.tv3.cat/720/el7ecamio5capitol1__H264_720.mp4" , "http://hd.tv3.cat/1080/el7ecamio5capitol1__H264_1080.mp4" , "http://www.tv3.cat/multimedia/jpg/2/2/1234374324022.jpg", "http://www.tv3.cat/multimedia/jpg/2/2/1234374324022.jpg", "http://www.tv3.cat/multimedia/jpg/2/2/1234374324022.jpg", "Uns caçadors de tresors francesos investiguen si hi ha or a la zona de la Vajol." , "" , "49 mgb.", "99 mgb.", "El tresor del setè camió", "http://www.tv3.cat/multimedia/gif/5/8/1230554823185.gif", "http://www.tv3.cat/multimedia/jpg/3/9/1230554796793.jpg", "Docusèrie" , "http://www.tv3.cat/programa/240582695/El-tresor-del-7e-camio" , "http://www.tv3.cat/multimedia/jpg/5/5/1234374299055.jpg" , "Fitxa del programa", "20090211");
            
        server = "directo"
        patron = 'addItemToVideoList\((.*?)\);'
        matches = re.compile(patron,re.DOTALL).findall(data)
        for match in matches:
            try:
                patron = '"(.*?)"'
                items = re.compile(patron,re.DOTALL).findall(match)
                
                video_720 = items[2].replace(" ","%20")
                video_1080 = items[3].replace(" ","%20")
                scrapedthumbnail = items[4]
                scrapedtitle = items[14] + " - " + items[11] + " (" + items[0] + ")"
                scrapedplot = items[7]
                
                # Anade el video en 720p
                itemlist.append( Item(channel=__channel__, action="play" , title= scrapedtitle + " (720p)", url=video_720, thumbnail=scrapedthumbnail, plot=scrapedplot, server=server, extra="", category=item.category, fanart=scrapedthumbnail, folder=False))
                itemlist.append( Item(channel=__channel__, action="play" , title=scrapedtitle + " (1080p)", url=video_1080, thumbnail=scrapedthumbnail, plot=scrapedplot, server=server, extra="", category=item.category, fanart=scrapedthumbnail, folder=False))
            except:
                import sys
                for line in sys.exc_info():
                    logger.error( "%s" % line )     
        
        
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
    return itemlist

def links(item): 
    logger.info("[tv3.py] links")   
     
    server = "directo"   
    itemlist = []
    try:
        # --------------------------------------------------------
        # Saca el codigo de la URL y descarga
        # --------------------------------------------------------
        patron = "/videos/(\d+)/"
        matches = re.compile(patron,re.DOTALL).findall(item.url)
        scrapertools.printMatches(matches)
        codigo = matches[0]
    
        # Prueba con el modo 1
        url = geturl3(codigo)
        if url=="" or url == None:
            url = geturl1(codigo)
        if url=="" or url == None:
            url = geturl2(codigo)
        if url=="" or url == None:
            url = geturl4(codigo)
        
        if url=="" or url == None:
            return []
        
        if url.startswith("http"):
            itemlist.append( Item(channel=__channel__, action="play" , title="play", url=url, thumbnail=item.thumbnail, plot=item.plot, server=server, extra="", category=item.category, fanart=item.thumbnail, folder=False))
        else:
            #url = "rtmp://mp4-500-str.tv3.cat/ondemand/mp4:g/tvcatalunya/3/1/1269579524113.mp4"
            patron = "rtmp\:\/\/([^\/]+)\/ondemand\/mp4\:(g\/.*?mp4)"
            matches = re.compile(patron,re.DOTALL).findall(url)
            media = matches[0][1]
            
            videourl = "http://mp4-medium-dwn.media.tv3.cat/" + media
            itemlist.append( Item(channel=__channel__, action="play" , title="play", url=videourl, thumbnail=item.thumbnail, plot=item.plot, server=server, extra="", category=item.category, fanart=item.thumbnail, folder=False))
    except:  
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line ) 
                
        
    return itemlist

def geturl1(codigo):
    #http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID=1594629&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=FLV&rnd=481353"
    logger.info("[tv3.py] geturl1 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
    	url = matches[0]
    	url = url.replace('rtmp://flv-500-str.tv3.cat/ondemand/g/','http://flv-500.tv3.cat/g/')
    return url

def geturl2(codigo):
    #http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID=1594629&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474"
    logger.info("[tv3.py] geturl2 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
    	url = matches[0]
    	url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
	return url

def geturl3(codigo):
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=MP4"
    logger.info("[tv3.py] geturl3 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
    	url = matches[0]
    	#url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

def geturl4(codigo):
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=MP4GES&RP=www.tv3.cat"
    logger.info("[tv3.py] geturl4 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
    	url = matches[0]
    	#url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

