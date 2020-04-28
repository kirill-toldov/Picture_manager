import os
import tkinter as tk
from PIL import Image,ImageTk
from tkinter import filedialog as fd
import json

import nltk
import string
from nltk.corpus import stopwords

from langdetect import detect
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize

import pytesseract
from pytesseract import image_to_string
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

import cv2




class Img():
    def __init__(self,img_name,img_dir):
        self._name=img_name.lower()
        self._dir=(img_dir+ '\\' + img_name).lower()
        self._tags=[]
        self._img=Image.open(self.get_dir())

        self.update()
        
        self.read_tags()
        self.read_text()
        
    
    def update(self):
        with open('tag_file.json') as file:
                f=json.load(file)
                new=True
                for i in range(len(f)):
                    if f[i]["dir"] == self.get_dir():
                        new=False
                        break
                if new:
                    print('Обновляю информацию о картинке '+self._name);
                    with open('tag_file.json') as file:
                        f=json.load(file)
                    rus=pytesseract.image_to_string(self.get_img(),lang='rus').lower()
                    rus=[i for i in nltk.word_tokenize(rus) if i not in string.punctuation]
                    eng=pytesseract.image_to_string(self.get_img(),lang='eng').lower()
                    eng=[i for i in nltk.word_tokenize(eng) if i not in string.punctuation]
                    f+=[{'dir':self.get_dir().lower(),'tags':[],'rus_text':rus,'eng_text':eng}]
                    with open('tag_file.json','w') as file:
                        try:
                            json.dump(f,file,ensure_ascii=False)
                        except:
                            print("В файле "+self._dir+" произошла ошибка при чтении текста.")
                            file.write(']}]')
    

    def filter(self):
        #img=cv2.medianBlur(img,5)
        None

    def get_img(self):
        return self._img

    def read_text(self):
        with open('tag_file.json') as file:
                f=json.load(file)
                for i in range(len(f)):
                    if f[i]["dir"] == self.get_dir():
                        try:
                            self._rus_text=f[i]['rus_text']
                        except:
                            print(self.get_name())
                        self._eng_text=f[i]['eng_text']
                        break
       

    def get_text(self,lang):
        if lang=='ru':
            return self._rus_text
        else:
            return self._eng_text
    
    def get_tags(self):
        return self._tags
    
    def read_tags(self):
        try:
            with open('tag_file.json') as file:
                tags=json.load(file)
                for i in range(len(tags)):
                    if tags[i]["dir"] == self.get_dir():
                        #print('Читаю теги картинки '+ self._name+':'+str(tags[i]["tags"]))
                        self._tags=tags[i]["tags"]
                        break
        except:
            None
                
    def get_name(self):
        return self._name
    def get_dir(self):
        return self._dir

class Catalog():
    def __init__(self,root=None,dirs=[],files=None,prev=None):
        self._dir=root
        self._dirs=dirs
        self._files=files
        self._prev=prev
        
    def get_dir(self):
        return self._dir
    def get_dirs(self):
        return self._dirs
    def get_files(self):
        return self._files
    def get_name(self):
        return self._dir.split('\\')[-1]
    def get_all(self):
        return self._dirs+self._files
    def set_prev(self,new_prev):
        self._prev=new_prev
    def get_prev(self):
        return self._prev

    def if_img(self,file):
        ext_list=['.jpg','.jpeg','.png']
        for i in ext_list:
            if file.endswith(i):
                return True
        return False


    def find_images(self,start_dir):
        img_list=[]
        for root, dirs, files in os.walk(start_dir):
            
            
            #for d in dirs:
             #   img_list.extend(find_images(d))
        
            #print(files)
            for file in files:
                if self.if_img(file):
                    img_list.append(Img(file,root))
        return img_list

    def find_folders(self,start_dir):
        walk=[]
        for root, dirs, files in os.walk(start_dir):
            walk+=[[root,dirs,files]]
        
        self.catalog_list=[]
        self.img_list=[]

        for root,dirs,files in reversed(walk):
            file_list=[]
            for file in files:
                if self.if_img(file):
                     file_list+=[Img(file,root)]
                     self.img_list+=[file_list[-1]]

            dir_list=[]
            for d in dirs:
                 for i in self.catalog_list:
                    if root+'\\'+d==i.get_dir():
                        dir_list+=[i]
            self.catalog_list=[Catalog(root,dir_list,file_list,None)]+self.catalog_list

            
        self.catalog_list[0].set_prev(self.catalog_list[0])
        for i in self.catalog_list[1::]:
            j=0
            while not(i in self.catalog_list[j].get_dirs()):
                j+=1
            i.set_prev(self.catalog_list[j])
        return self.catalog_list
    


class Window:
    def __init__(self,cat):

        self.inf_open=0

        self.cat=cat

        self.current_dir=cat[0]
        
        self.window=tk.Tk()
        self.window.attributes('-fullscreen', False)

        self.canvas = tk.Canvas(self.window)
        self.canvas.grid(row=0, column=0)

        self.search_entry=tk.Entry(self.canvas)
        self.search_entry.grid(row=0,column=0)

        self.search_button=tk.Button(self.canvas,text='Поиск',command=self.search)
        self.search_button.grid(row=0,column=1)

        self.listbox = tk.Listbox(self.canvas)
        self.show_catalog(cat[0])
        self.listbox.grid(row=1, column=0)

        self.preview=tk.Canvas(self.window)
        self.preview.grid(row=0, column=1)

        self.show_preview("folder.jpg")

        #self.show_img_button=tk.Button(self.canvas,text='Открыть изображение',command=self.show_img)
        #self.show_img_button.grid(row=2,column=0)

        self.exit_button=tk.Button(self.window,text='Выход',command=self.window.destroy)
        self.exit_button.grid(row=1, column=1)

        self.inf_button=tk.Button(self.canvas,text='Информация',command=self.inf)
        self.inf_button.grid(row=2, column=0)


        self.window.bind('<Return>', self.enter)


        self.refresh()

        self.window.mainloop()

    def show_img(self):
        self.cur_obj.get_img().show()
        
    def normal_form(self,s,lang):

        if s=='':
            return []

        s=s.lower()
        
        if lang == 'ru':
            lang='russian'
        else:
            lang='english'

        stemmer = SnowballStemmer(lang)

        s=[i for i in nltk.word_tokenize(s) if i not in string.punctuation]
        #and i not in stopwords.words(lang)
        
        s=[stemmer.stem(word) for word in s]

        return s


    def search(self):

        find_list=[]

        
        s=self.search_entry.get().lower()

        if s=='':
            return None

        lang='ru'

        for i in s:
            if 97<=ord(i)<=122:
                lang='en'
                break
            #if 1072<=ord(i)<=1103:
                #lang='ru'
                #break
            #return None

        s=self.normal_form(s,lang)
                    
        for img in start.img_list:
            name=img.get_name().split('.')[0::-2][0].lower()
            tags=' '.join(img.get_tags()).lower()
            text=' '.join(img.get_text(lang))

            for i in self.search_entry.get().lower().split():
                if i in name or i in tags or i in text:
                    find_list+=[img]
                    break

                name=self.normal_form(name,lang)
                #print(name)
                #print(text)
                tags=self.normal_form(tags,lang)
                text=self.normal_form(text,lang)
                
                for i in s:
                    if i in name or i in tags or i in text:
                        if img not in find_list:
                            find_list+=[img]
                            break


        
        self.current_dir=Catalog(None,[],find_list,self.cat[0])

        self.listbox.delete(0,self.listbox.size())
        self.listbox.insert(0,'..')

        for line in find_list:
            self.listbox.insert(tk.END,' '+line.get_name())

        self.search_entry.delete(0,tk.END)



                
        #print([i.get_name() for i in find_list])
            

    def inf(self):
        if self.inf_open==1:
            return None
        else:
            self.inf_open=1
        pos=self.pos
        if pos!=-1:
            #self.cur_obj=self.current_dir.get_all()[pos]
            if type(self.cur_obj) == Img:
                self.inf_window=tk.Tk()

                self.inf_window.title(str(self.cur_obj.get_name()))


                self.tag_entry=tk.Entry(self.inf_window)
                self.tag_entry.grid(row=0,column=0)

                self.add_tag_button=tk.Button(self.inf_window,text='Добавить тег',command=self.add_tag)
                self.add_tag_button.grid(row=0,column=1)

                self.tag_listbox=tk.Listbox(self.inf_window)
                with open("tag_file.json") as file:
                    tags=json.load(file)
                    end=1
                    for i in range(len(tags)):
                        if tags[i]["dir"] == self.cur_obj.get_dir():
                            end=0
                            break
                    if end == 0:
                        for i in tags[i]["tags"]:
                            self.tag_listbox.insert(0,i)
                self.tag_listbox.grid(row=1,column=0)

                self.delete_tag_button=tk.Button(self.inf_window,text='Удалить тег',command=self.delete_tag)
                self.delete_tag_button.grid(row=1,column=1)

                self.save_button=tk.Button(self.inf_window,text='Сохранить и выйти',command=self.save)
                self.save_button.grid(row=2, column=0)
                    

                self.exit_button=tk.Button(self.inf_window,text='Отмена',command=self.exit_inf)
                self.exit_button.grid(row=2, column=1)
                    
                self.inf_window.mainloop()


    def exit_inf(self):
        self.inf_open=0
        self.inf_window.destroy()

    def save(self):
        #pos=self.listbox.curselection()[0]-1
        #obj=self.current_dir.get_all()[pos]
        try:
            with open('tag_file.json') as file:
                tags=json.load(file)
                for i in range(len(tags)):
                    if tags[i]["dir"] == self.cur_obj.get_dir():
                        tags.pop(i)
                        break
        except:
            tags=[]

        tags+=[{"dir": self.cur_obj.get_dir(),"tags": self.tag_listbox.get(0,tk.END),"rus_text":self.cur_obj.get_text('ru'),"eng_text":self.cur_obj.get_text('en')}]
        with open('tag_file.json','w') as file:
            json.dump(tags,file,ensure_ascii=False)
        self.exit_inf()
            
    def add_tag(self):
        if self.tag_entry.get()!= '':
            self.tag_listbox.insert(tk.END,self.tag_entry.get().lower())
            self.tag_entry.delete(0,tk.END)

    def delete_tag(self):
        try:
            self.tag_listbox.delete(self.tag_listbox.curselection())
        except:
            None
        

    def show_catalog(self,folder):
        self.listbox.delete(0,self.listbox.size())
        self.listbox.insert(0,'..')
        for line in folder.get_dirs():
            self.listbox.insert(tk.END,'[f] '+line.get_name())
        for line in folder.get_files():
            self.listbox.insert(tk.END,' '+line.get_name())

    def show_preview(self,img_dir):
        self.pilImage = Image.open(img_dir)
        self.pilImage.thumbnail((200,200))
        self.image = ImageTk.PhotoImage(self.pilImage)
        imagesprite = self.preview.create_image(100,116,image=self.image)

    def enter(self,event):
        try:
            pos=self.listbox.curselection()[0]-1
            if pos==-1:
                self.open_folder(pos)
            else:
                obj=self.current_dir.get_all()[pos]
                if type(obj) == Catalog:
                    self.open_folder(pos)
                else:
                    self.show_img()
        except:
            None


    def open_folder(self,pos):
        #pos=self.listbox.curselection()[0]-1
        if pos==-1:
            self.current_dir=self.current_dir.get_prev()
            self.show_catalog(self.current_dir)
        else:
            obj=self.current_dir.get_all()[pos]
            if type(obj) == Catalog:
                self.current_dir=obj
                self.show_catalog(obj)

    def refresh(self):
        if len(self.listbox.curselection())!=0:
            self.pos=self.listbox.curselection()[0]-1
            self.cur_obj=self.current_dir.get_all()[self.pos]
            if self.pos == -1 or type(self.cur_obj)==Catalog:
                self.show_preview("folder.jpg")
            else:
                self.show_preview(self.cur_obj.get_dir())
        self.window.after(100, self.refresh)
            

catalog1='.\catalog'
catalog2='.\Haibane Renmei'
catalog3='.\gatari'


for root, dirs, files in os.walk('./'):
    f=files
    break
if 'tag_file.json' not in f:
    print('Создаю файл.')
    with open('tag_file.json', 'w') as file:
        file.write('[]')  


start=Catalog()


l=start.find_folders(catalog3)


Window(l)
    















    

