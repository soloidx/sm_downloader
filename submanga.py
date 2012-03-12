"""
Submanga Core
Submanga downloader
usage:
"""

import os, sys
import urllib2
from os import path


from pyquery import PyQuery as pq

ROOT_PATH = path.realpath(path.dirname(__file__))

class SubmangaPage(object):
    """Core for submanga page object"""
    def __init__(self, page):
        super(SubmangaPage, self).__init__()
        self.base_url = page
        self.name = page.split('/')[-1]
        num_cut = (len(self.name)+1)*-1
        self.host = page[:num_cut]
        self.output_dir = ROOT_PATH + '/library/' + self.name
        if not os.path.exists(self.output_dir):
            print 'creando directorio de manga %s' % self.name
            #crea un directorio con el nombre del manga
            os.makedirs(self.output_dir)
        else:
            print 'accediendo a %s' % self.name
        self.get_chapters()

    def get_chapters(self):
        """
        obtiene los capiulos de las paginas con sus urls
        """
        pagina_completa = pq(self.base_url+'/completa')
        #hago una busqueda con pyquery y devuelo el valor de las urls
        capitulos = [capitulo.values()[-1] for capitulo in \
                pagina_completa('table.caps tr td.s a')]
        print 'capitulos obtenidos total: %i' % len(capitulos)
        self.make_directories_and_download(capitulos)

    def make_directories_and_download(self, url_list):
        url_list.reverse()
        for address in  url_list:
            cap_id = address.split('/')[-1]
            cap_name = address.split('/')[-2]
            cap_dir = self.output_dir + '/' + cap_name
            if not os.path.exists(cap_dir):
                os.makedirs(cap_dir)
                print 'creando directorio %s' % cap_dir
            #descargo cada capitulo
            print 'procesando %s' % cap_name
            self.process_page_and_download(cap_id, cap_dir)

    def process_page_and_download(self, page_id, page_dir):
        page_url = self.host + '/c/' + page_id
        page_processed = pq(page_url)
        select = page_processed('select option')
        url_first = ''
        for en in page_processed('body div a img'):
            url_first = en.values()[-1]
        #obtengo la url de descarga base
        temp_filename = url_first.split('/')[-1]
        url_down_base = url_first[:len(temp_filename)*-1]

        #descargo la imagen de cada capitulo
        for i in range(1, len(select)+1):
            address = url_down_base + str(i) + '.jpg'
            filename = page_dir + '/' + str(i) + '.jpg'
            print 'bajando %i de %i' % (i, len(select))
            self.download_image(address, filename)

    def download_image(self, img_url, filename):
        print '%s --> %s' % (img_url, filename)
        if not os.path.exists(filename):
            try:
                resp = urllib2.urlopen(img_url)
                file_photo = open(filename, 'w')
                file_photo.write(resp.read())
            except:
                pass
