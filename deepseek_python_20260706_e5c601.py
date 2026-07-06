#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
import struct
import threading
import time
import random
import string
import re

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'; RESET_ALL = '\033[0m'

os.system('clear' if os.name == 'posix' else 'cls')

BANNER = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════════════╗
{Fore.RED}║  {Fore.CYAN}██████╗  ██████╗ ████████╗    ██████╗  ██████╗ ████████╗{Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██╔══██╗██╔═══██╗╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝{Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██████╔╝██║   ██║   ██║       ██████╔╝██║   ██║   ██║   {Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██╔══██╗██║   ██║   ██║       ██╔══██╗██║   ██║   ██║   {Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██████╔╝╚██████╔╝   ██║       ██████╔╝╚██████╔╝   ██║   {Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}╚═════╝  ╚═════╝    ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   {Fore.RED}    ║
{Fore.RED}║  {Fore.YELLOW}════════════════════════════════════════════════════════════════════{Fore.RED} ║
{Fore.RED}║  {Fore.GREEN}╔══════════════════════════════════════════════════════════════════╗ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  🤖 MCBOT v4.0 - SIMPLE Y FUNCIONAL                            ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  📡 SE CONECTA, REGISTRA Y MUESTRA EL CHAT                    ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  💬 ESCRIBE Y EL BOT HABLA                                     ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}╚══════════════════════════════════════════════════════════════════╝ {Fore.RED}║
{Fore.RED}╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

print(BANNER)
print("")

def generar_nombre():
    nombres = ['Bot', 'Auto', 'Pepe', 'Juan', 'Luis', 'Ana', 'Maria', 'Carlos', 
               'Pedro', 'Pablo', 'Diego', 'Laura', 'Sofia', 'Jose', 'Manuel']
    return random.choice(nombres) + ''.join(random.choices(string.digits, k=3))

class Bot:
    def __init__(self, ip, puerto, nombre, password):
        self.ip = ip
        self.puerto = puerto
        self.nombre = nombre
        self.password = password
        self.socket = None
        self.conectado = False
        self.running = True
        self.registrado = False
        self.id_cliente = random.randint(0, 2**64-1)
        self.jugadores = []
        self.play_activo = False
        
        self.MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        self.ID_LOGIN = 0x01
        self.ID_PLAY_STATUS = 0x02
        self.ID_TEXT = 0x09
        self.ID_MOVE_PLAYER = 0x13
        self.ID_DISCONNECT = 0x05
        self.ID_RESOURCE_PACKS_CLIENT_RESPONSE = 0x08
    
    def conectar(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(3)
            
            print(f"{Fore.CYAN}[🔌]{Fore.RESET} Conectando a {Fore.GREEN}{self.ip}:{self.puerto}{Fore.RESET}")
            
            ping = bytearray()
            ping.extend(b'\x01')
            ping.extend(struct.pack('>Q', int(time.time())))
            ping.extend(self.MAGIC)
            ping.extend(b'\x00' * 8)
            self.socket.sendto(bytes(ping), (self.ip, self.puerto))
            
            data, addr = self.socket.recvfrom(2048)
            
            if len(data) > 0:
                print(f"{Fore.GREEN}[✅]{Fore.RESET} Servidor respondió!")
                self._enviar_login()
                return True
            
            return False
            
        except socket.timeout:
            print(f"{Fore.RED}[❌]{Fore.RESET} Timeout - Servidor no responde")
            return False
        except Exception as e:
            print(f"{Fore.RED}[❌]{Fore.RESET} Error: {e}")
            return False
    
    def _enviar_login(self):
        packet = bytearray()
        packet.append(self.ID_LOGIN)
        
        data = bytearray()
        data.extend(struct.pack('>I', 130))
        data.extend(struct.pack('>I', 0))
        
        nombre_bytes = self.nombre.encode('utf-8')
        data.extend(struct.pack('>H', len(nombre_bytes)))
        data.extend(nombre_bytes)
        
        data.extend(b'\x00' * 8)
        data.extend(struct.pack('>Q', self.id_cliente))
        data.extend(b'\x00' * 64)
        data.extend(b'\x00')
        
        packet.extend(struct.pack('>I', len(data)))
        packet.extend(data)
        
        self.socket.sendto(bytes(packet), (self.ip, self.puerto))
        print(f"{Fore.CYAN}[🔑]{Fore.RESET} Conectando como {Fore.GREEN}{self.nombre}{Fore.RESET}")
        
        time.sleep(1)
        self._responder_resource_packs()
    
    def _responder_resource_packs(self):
        try:
            packet = bytearray()
            packet.append(self.ID_RESOURCE_PACKS_CLIENT_RESPONSE)
            packet.extend(struct.pack('>B', 2))
            packet.extend(b'\x00' * 8)
            self.socket.sendto(bytes(packet), (self.ip, self.puerto))
        except:
            pass
    
    def enviar_mensaje(self, texto):
        if not self.socket:
            print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} No conectado")
            return
        
        try:
            packet = bytearray()
            packet.append(self.ID_TEXT)
            packet.append(0x01)
            packet.extend(b'\x00')
            
            msg = texto.encode('utf-8')
            packet.extend(struct.pack('>I', len(msg)))
            packet.extend(msg)
            
            packet.extend(b'\x00' * 4)
            packet.extend(b'\x00')
            packet.extend(b'\x00')
            
            self.socket.sendto(bytes(packet), (self.ip, self.puerto))
            
        except Exception as e:
            print(f"{Fore.RED}[❌]{Fore.RESET} Error: {e}")
    
    def enviar_comando(self, comando):
        self.enviar_mensaje(comando)
    
    def mover(self):
        if not self.socket:
            return
        
        try:
            packet = bytearray()
            packet.append(self.ID_MOVE_PLAYER)
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 1.6))
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 0.0))
            self.socket.sendto(bytes(packet), (self.ip, self.puerto))
        except:
            pass
    
    def escuchar(self):
        ultimo = time.time()
        
        while self.running:
            try:
                if self.socket:
                    self.socket.settimeout(1.0)
                    data, addr = self.socket.recvfrom(4096)
                    
                    if data:
                        self._procesar_paquete(data)
                    
                    if time.time() - ultimo > 3:
                        self.mover()
                        ultimo = time.time()
                else:
                    time.sleep(1)
                    
            except socket.timeout:
                self.mover()
                continue
            except:
                continue
    
    def _procesar_paquete(self, data):
        try:
            packet_id = data[0]
            
            if packet_id == self.ID_TEXT:
                self._procesar_texto(data)
            elif packet_id == self.ID_PLAY_STATUS:
                self._procesar_status(data)
            elif packet_id == self.ID_DISCONNECT:
                print(f"{Fore.RED}[❌]{Fore.RESET} Desconectado")
                self.running = False
                
        except:
            pass
    
    def _procesar_texto(self, data):
        try:
            offset = 1
            tipo = data[offset]
            offset += 1
            
            if tipo == 0:
                largo = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                msg = data[offset:offset+largo].decode('utf-8', errors='ignore')
                
                print(f"{Fore.MAGENTA}[📡]{Fore.RESET} {msg}")
                
                if "registered" in msg.lower():
                    self.registrado = True
                    print(f"{Fore.GREEN}[✅]{Fore.RESET} Registrado!")
                
                elif "logged in" in msg.lower():
                    self.registrado = True
                    print(f"{Fore.GREEN}[✅]{Fore.RESET} Login exitoso!")
                
                # Detectar jugadores
                if "joined" in msg.lower():
                    if self.play_activo:
                        print(f"{Fore.GREEN}[➕]{Fore.RESET} {Fore.CYAN}{msg}{Fore.RESET}")
                
                if "left" in msg.lower():
                    if self.play_activo:
                        print(f"{Fore.RED}[➖]{Fore.RESET} {Fore.CYAN}{msg}{Fore.RESET}")
                
                # Lista de jugadores
                if "players" in msg.lower() and "online" in msg.lower():
                    self._mostrar_lista(msg)
                
            elif tipo == 1:
                largo = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                nombre = data[offset:offset+largo].decode('utf-8', errors='ignore')
                offset += largo
                
                largo = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                msg = data[offset:offset+largo].decode('utf-8', errors='ignore')
                
                print(f"{Fore.YELLOW}[💬]{Fore.RESET} {Fore.CYAN}{nombre}{Fore.RESET}: {msg}")
                
        except:
            pass
    
    def _mostrar_lista(self, msg):
        try:
            match = re.search(r'(\d+)\s*players?\s+online:?\s*(.*)', msg, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                players_str = match.group(2).strip()
                if players_str:
                    self.jugadores = [p.strip() for p in players_str.split(',') if p.strip()]
                    print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════════════════════")
                    print(f"{Fore.CYAN}[👥]{Fore.RESET} {Fore.YELLOW}{count}{Fore.RESET} jugadores online:")
                    for i, p in enumerate(self.jugadores, 1):
                        print(f"  {Fore.GREEN}{i}.{Fore.RESET} {Fore.CYAN}{p}{Fore.RESET}")
                    print(f"{Fore.CYAN}═══════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
        except:
            pass
    
    def _procesar_status(self, data):
        try:
            status = data[1]
            if status == 0:
                print(f"{Fore.GREEN}[✅]{Fore.RESET} Conectado!")
                self.conectado = True
                time.sleep(1)
                self.enviar_comando("/list")
            elif status == 1:
                print(f"{Fore.RED}[❌]{Fore.RESET} Ya estás conectado")
            elif status == 2:
                print(f"{Fore.RED}[❌]{Fore.RESET} Servidor lleno")
            elif status == 3:
                print(f"{Fore.RED}[❌]{Fore.RESET} Servidor offline")
            elif status == 4:
                print(f"{Fore.RED}[❌]{Fore.RESET} Versión incorrecta")
        except:
            pass
    
    def cerrar(self):
        self.running = False
        if self.socket:
            self.socket.close()
        print(f"{Fore.YELLOW}[🔌]{Fore.RESET} Desconectado")

def main():
    print(f"\n{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.CYAN}     📡 CONFIGURACIÓN")
    print(f"{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
    
    ip = input(f"{Fore.GREEN}[?]{Fore.RESET} IP o dominio: ").strip()
    if not ip:
        print(f"{Fore.RED}[!]{Fore.RESET} IP requerida")
        sys.exit(1)
    
    try:
        puerto = int(input(f"{Fore.GREEN}[?]{Fore.RESET} Puerto: ").strip())
    except:
        print(f"{Fore.RED}[!]{Fore.RESET} Puerto inválido")
        sys.exit(1)
    
    nombre = input(f"{Fore.GREEN}[?]{Fore.RESET} Nombre (ENTER para aleatorio): ").strip()
    if not nombre:
        nombre = generar_nombre()
    print(f"{Fore.CYAN}[🤖]{Fore.RESET} Nombre: {Fore.GREEN}{nombre}{Fore.RESET}")
    
    password = input(f"{Fore.GREEN}[?]{Fore.RESET} Contraseña: ").strip()
    if not password:
        print(f"{Fore.RED}[!]{Fore.RESET} Contraseña requerida")
        sys.exit(1)
    
    print(f"\n{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.CYAN}     🔌 CONECTANDO...")
    print(f"{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
    
    bot = Bot(ip, puerto, nombre, password)
    
    if not bot.conectar():
        print(f"{Fore.RED}[❌]{Fore.RESET} No se pudo conectar!")
        sys.exit(1)
    
    time.sleep(2)
    
    print(f"{Fore.CYAN}[🔐]{Fore.RESET} Registrando...")
    bot.enviar_comando(f"/login {password}")
    time.sleep(1)
    
    if not bot.registrado:
        bot.enviar_comando(f"/register {password}")
        time.sleep(1)
        bot.enviar_comando(f"/login {password}")
        time.sleep(1)
    
    hilo = threading.Thread(target=bot.escuchar, daemon=True)
    hilo.start()
    
    print(f"\n{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.GREEN}[✅]{Fore.RESET} Bot ONLINE: {Fore.CYAN}{nombre}{Fore.RESET}")
    print(f"{Fore.GREEN}[📡]{Fore.RESET} CHAT EN VIVO ACTIVADO")
    print(f"{Fore.GREEN}[💬]{Fore.RESET} Escribe algo para enviar al chat")
    print(f"{Fore.GREEN}[👥]{Fore.RESET} Escribe {Fore.CYAN}/play{Fore.RESET} para ver cuando alguien se une")
    print(f"{Fore.GREEN}[👥]{Fore.RESET} Escribe {Fore.CYAN}/play off{Fore.RESET} para desactivar")
    print(f"{Fore.GREEN}[📋]{Fore.RESET} Escribe {Fore.CYAN}/list{Fore.RESET} para ver jugadores")
    print(f"{Fore.GREEN}[🚪]{Fore.RESET} Escribe {Fore.RED}/exit{Fore.RESET} para salir")
    print(f"{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
    
    try:
        while bot.running:
            texto = input(f"{Fore.CYAN}[📝 Escribe algo:]{Fore.RESET} ")
            
            if not texto.strip():
                continue
            
            if texto.lower() == '/exit':
                bot.enviar_mensaje("Me voy! Hasta luego! 👋")
                bot.cerrar()
                break
            
            if texto.lower() == '/play':
                bot.play_activo = True
                print(f"{Fore.GREEN}[👥]{Fore.RESET} Monitoreo ACTIVADO")
                continue
            
            if texto.lower() == '/play off':
                bot.play_activo = False
                print(f"{Fore.YELLOW}[👥]{Fore.RESET} Monitoreo DESACTIVADO")
                continue
            
            if texto.lower() == '/list':
                bot.enviar_comando("/list")
                print(f"{Fore.CYAN}[📋]{Fore.RESET} Solicitando lista...")
                continue
            
            bot.enviar_mensaje(texto)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!]{Fore.RESET} Interrumpido")
        bot.enviar_mensaje("Me voy! Hasta luego! 👋")
        bot.cerrar()
    
    print(f"{Fore.GREEN}[✅]{Fore.RESET} Bot cerrado")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}[❌]{Fore.RESET} Error: {e}")
        sys.exit(1)