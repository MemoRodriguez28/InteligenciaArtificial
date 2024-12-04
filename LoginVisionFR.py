from tkinter import *
from tkinter import messagebox
import os
import cv2
import face_recognition
import pickle

# ------------------ Función para mostrar mensaje de éxito ---------------------
def mostrar_ingreso_correcto(mensaje):
    global pantalla3
    pantalla3 = Toplevel(pantalla)
    pantalla3.title("Éxito")
    pantalla3.geometry("300x200")
    pantalla3.configure(bg="white")

    Label(pantalla3, text=mensaje, bg="white", fg="blue", font=("Calibri", 14, "bold")).pack(pady=50)
    Button(pantalla3, text="Cerrar", command=pantalla3.destroy, bg="blue", fg="white", font=("Calibri", 12)).pack(pady=10)

# ------------------ Función para registrar datos faciales ---------------------
def registrar_facial_completo(usuario, contra):
    if not usuario or not contra:
        Label(pantalla4, text="Todos los campos son obligatorios", fg="red", font=("Calibri", 11)).pack()
        return

    if len(contra) < 8:
        Label(pantalla4, text="La contraseña debe tener al menos 8 caracteres", fg="red", font=("Calibri", 11)).pack()
        return

    messagebox.showinfo("Instrucciones", "Presiona la tecla 'Espacio' para capturar tu foto. Presiona 'Esc' para cancelar.")

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Captura de Rostro")

    while True:
        ret, frame = cap.read()
        if not ret:
            Label(pantalla4, text="Error al acceder a la cámara", fg="red", font=("Calibri", 11)).pack()
            break

        cv2.imshow("Captura de Rostro", frame)

        key = cv2.waitKey(1)
        if key == 32:  # Barra espaciadora
            img_path = usuario + ".jpg"
            cv2.imwrite(img_path, frame)
            Label(pantalla4, text="Imagen capturada exitosamente", fg="blue", font=("Calibri", 11)).pack()
            break
        elif key == 27:  # Esc para cancelar
            Label(pantalla4, text="Captura cancelada", fg="red", font=("Calibri", 11)).pack()
            break

    cap.release()
    cv2.destroyAllWindows()

    if os.path.exists(img_path):
        with open(usuario + "_data.txt", "w") as archivo:
            archivo.write(usuario + "\n")
            archivo.write(contra)

        img = face_recognition.load_image_file(img_path)
        face_encodings = face_recognition.face_encodings(img)
        if len(face_encodings) == 0:
            Label(pantalla4, text="No se detectó rostro", fg="red", font=("Calibri", 11)).pack()
        else:
            with open(usuario + "_encoding.pkl", "wb") as file:
                pickle.dump(face_encodings[0], file)
            mostrar_ingreso_correcto("Registro facial exitoso")

# ------------------ Función para verificar rostro en inicio de sesión ---------------------
def verificar_rostro(usuario):
    if not os.path.exists(usuario + "_encoding.pkl"):
        Label(pantalla2, text="Usuario no registrado o sin datos faciales", fg="red", font=("Calibri", 11)).pack()
        return

    messagebox.showinfo("Instrucciones", "Presiona la tecla 'Espacio' para tomar la foto.")

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Verificación de Rostro")

    usuario_data = pickle.load(open(usuario + "_encoding.pkl", "rb"))
    reconocido = False
    tolerance = 0.4  # Reducir la tolerancia para ser más estricto

    while True:
        ret, frame = cap.read()
        if not ret:
            Label(pantalla2, text="Error al acceder a la cámara", fg="red", font=("Calibri", 11)).pack()
            cap.release()
            cv2.destroyAllWindows()
            return

        cv2.imshow("Verificación de Rostro", frame)

        key = cv2.waitKey(1)
        if key == 32:  # Tecla Espacio
            img_path = "comparacion_temp.jpg"
            cv2.imwrite(img_path, frame)
            break
        elif key == 27:  # Tecla Esc para salir
            cap.release()
            cv2.destroyAllWindows()
            return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_frame)

    if os.path.exists(img_path):
        os.remove(img_path)

    if face_encodings:
        match = face_recognition.compare_faces([usuario_data], face_encodings[0], tolerance=tolerance)
        if match[0]:
            reconocido = True

    cap.release()
    cv2.destroyAllWindows()

    if reconocido:
        mostrar_ingreso_correcto(f"Bienvenido, {usuario}")
    else:
        Label(pantalla2, text="No se reconoció el rostro", fg="red", font=("Calibri", 11)).pack()

# ------------------ Pantalla de registro facial ---------------------
def registro_facial():
    global pantalla4, usuario_facial, contra_facial
    pantalla4 = Toplevel(pantalla)
    pantalla4.title("Registro Facial")
    pantalla4.geometry("400x400")
    pantalla4.configure(bg="white")

    usuario_facial = StringVar()
    contra_facial = StringVar()

    Label(pantalla4, text="Registro Facial", bg="white", font=("Calibri", 14, "bold")).pack(pady=10)
    Label(pantalla4, text="Usuario *", bg="white", font=("Calibri", 12)).pack()
    Entry(pantalla4, textvariable=usuario_facial, font=("Calibri", 12)).pack(pady=5)
    Label(pantalla4, text="Contraseña *", bg="white", font=("Calibri", 12)).pack()
    Entry(pantalla4, textvariable=contra_facial, show='*', font=("Calibri", 12)).pack(pady=5)

    Button(pantalla4, text="Capturar Rostro", command=lambda: registrar_facial_completo(usuario_facial.get(), contra_facial.get()), bg="blue", fg="white", font=("Calibri", 12)).pack(pady=20)

# ------------------ Pantalla principal ---------------------
def pantalla_principal():
    global pantalla
    pantalla = Tk()
    pantalla.geometry("400x500")
    pantalla.title("Sistema de Registro")
    pantalla.configure(bg="#f2f2f2")

    try:
        img_logo = PhotoImage(file="./Imagenes/Logo.png")
        img_logo = img_logo.subsample(4, 4)
        Label(pantalla, image=img_logo, bg="#f2f2f2").place(x=0, y=0)
    except TclError:
        Label(pantalla, text="No se pudo cargar el logo", bg="#f2f2f2", fg="red").place(x=10, y=10)

    Label(pantalla, text="Centro de Cómputo", bg="#003399", fg="white", width="300", height="3", font=("Calibri", 16, "bold")).pack()

    Label(pantalla, bg="#f2f2f2").pack()

    Button(pantalla, text="Iniciar sesión", height="2", width="30", command=login, bg="#003399", fg="white", font=("Calibri", 12)).pack(pady=10)
    Button(pantalla, text="Registro Facial", height="2", width="30", command=registro_facial, bg="#003399", fg="white", font=("Calibri", 12)).pack(pady=10)

    pantalla.mainloop()

# ------------------ Pantalla de login ---------------------
def login():
    global pantalla2
    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Login")
    pantalla2.geometry("400x300")
    pantalla2.configure(bg="white")

    verificacion_usuario = StringVar()

    Label(pantalla2, text="Iniciar sesión", bg="white", font=("Calibri", 14, "bold")).pack(pady=10)
    Label(pantalla2, text="Usuario *", bg="white", font=("Calibri", 12)).pack()
    Entry(pantalla2, textvariable=verificacion_usuario, font=("Calibri", 12)).pack(pady=5)

    Button(pantalla2, text="Verificar Rostro", command=lambda: verificar_rostro(verificacion_usuario.get()), bg="blue", fg="white", font=("Calibri", 12)).pack(pady=20)

pantalla_principal()
