import os
import re

# Словник для транслітерації (базова українська + часті російські "гості")
ukr_to_latin = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
    'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y',
    'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E',
    'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y',
    'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
    'Ш': 'Sh', 'Щ': 'Shch', 'Ь': '', 'Ю': 'Yu', 'Я': 'Ya',
    'ы': 'y', 'э': 'e', 'ё': 'yo', 'ъ': '', 'Ы': 'Y', 'Э': 'E', 'Ё': 'Yo', 'Ъ': ''
}

def transliterate(text):
    # Проходимось по кожній літері. Якщо вона є в словнику - міняємо, якщо ні (цифри, знаки) - залишаємо як є.
    return ''.join(ukr_to_latin.get(char, char) for char in text)

def rename_photos(directory):
    # Розширення файлів, які вважаємо фотографіями
    extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    
    # Заводимо мотор і їдемо по всіх файлах у вказаній папці
    for filename in os.listdir(directory):
        if filename.lower().endswith(extensions):
            # Перевіряємо, чи є хоч одна кирилична літера в назві
            if re.search('[а-яА-ЯіІїЇєЄґҐ]', filename):
                new_name = transliterate(filename)
                
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)
                
                # Перевіряємо, чи раптом такий файл вже не існує, щоб не було ДТП
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    print(f"Відрихтовано: {filename} -> {new_name}")
                else:
                    print(f"Увага: Файл {new_name} вже існує. Пропускаю {filename}, щоб не затерти.")

# Вкажи шлях до своєї папки замість крапки. Крапка - це поточна папка.
# Наприклад: rename_photos(r'C:\Users\Admin\Pictures\Photos')
target_dir = '.' 
rename_photos(target_dir)