"""
Submanga Core
Submanga downloader
usage:
"""

import os, sys
import urllib2
import zipfile
from os import path

from pyquery import PyQuery as pq

ROOT_PATH = path.realpath(path.dirname(__file__))


def zipfolder(path, relname, archive):
    paths = os.listdir(path)
    for p in paths:
        p1 = os.path.join(path, p) 
        p2 = os.path.join(relname, p)
        if os.path.isdir(p1): 
            zipfolder(p1, p2, archive)
        else:
            archive.write(p1, p2) 

def create_zip(path, relname, archname):
    archive = zipfile.ZipFile(archname, "w", zipfile.ZIP_DEFLATED)
    if os.path.isdir(path):
        zipfolder(path, relname, archive)
    else:
        archive.write(path, relname)
    archive.close()


class SubmangaPage(object):
    """Core for submanga page object"""
    def __init__(self, page):
        super(SubmangaPage, self).__init__()
        self.base_url = page
        self.name = page.split('/')[-1]
        num_cut = (len(self.name)+1)*-1
        self.host = page[:num_cut]
        self.output_dir = ROOT_PATH + '/library/' + self.name
        self.cbz_dir = ROOT_PATH + '/library/' + self.name + '/cbz/'
        if not os.path.exists(self.output_dir):
            print 'creando directorio de manga %s' % self.name
            #crea un directorio con el nombre del manga
            os.makedirs(self.output_dir)
        else:
            print 'accediendo a %s' % self.name
        if not os.path.exists(self.cbz_dir):
            os.makedirs(self.cbz_dir)
        self.get_chapters()

    def get_chapters(self):
        """
        get the page chapters with URLs
        """
        pagina_completa = pq(self.base_url+'/completa')
        #hago una busqueda con pyquery y devuelo el valor de las urls
        capitulos = [capitulo.values()[-1] for capitulo in \
                pagina_completa('table.caps tr td.s a')]
        print 'capitulos obtenidos total: %i' % len(capitulos)
        self.make_directories_and_download(capitulos)

    def make_directories_and_download(self, url_list):
        """
        creates the directories for each chapter
        """
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
            #cuando termine de descargar las imagenes crea un cbz con el
            #directorio
            self.compress_chapter(cap_name)
            
    def process_page_and_download(self, page_id, page_dir):
        """
        process the chapter page and generate the links for each image
        """
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
        cont = 0
        error = 0

        #si encuentra un archivo '.skip' en el directorio no
        #considera el capitulo
        if os.path.exists(page_dir + '/.skip'):
            return

        #es un numero de intentos arbitrarios en caso de que falle la
        #descarga
        while len(select) > cont and error < 5 * len(select):
            for i in range(1, len(select)+1):
                address = url_down_base + str(i) + '.jpg'
                filename = page_dir + '/' + str(i).rjust(4,'0') + '.jpg'
                print 'bajando %i de %i' % (i, len(select))
                resp = self.download_image(address, filename)
                if resp:
                    cont += 1
                else:
                    error += 1
                    cont = 0
        #una vez descargado e folder con las imagenes crea un archivo .skip para
        # que no vuelva a descargar el capitulo
        file_skip = open(page_dir + '/.skip', 'w')
        file_skip.close()

    def download_image(self, img_url, filename):
        """
        download a individual image
        """
        print '%s --> %s' % (img_url, filename)
        if not os.path.exists(filename):
            file_photo = open(filename, 'w')
            try:
                #este timeout es arbitrario, no me gusta esperar xP
                resp = urllib2.urlopen(img_url, timeout=60)
                file_photo.write(resp.read())
                file_photo.close()
                return 1
            except:
                #si no puede bajar el archivo lo borra
                file_photo.close()
                os.remove(filename)
                print 'fallo en la descarga'
                return 0
        return 1

    def compress_chapter(self, chapter_name):
        """
        compress a champther into a cbz
        """
        cap_dir = self.output_dir + '/' + chapter_name
        if chapter_name.isdigit():
            chapter_name = chapter_name.rjust(4,'0') #this is deliverated
        filename = self.cbz_dir + chapter_name + '.cbz'
        
        if os.path.exists(cap_dir) and not os.path.exists(filename):
            print 'comprimiendo capitulo...'
            create_zip(cap_dir, '', filename )
