from Modules.SistemaSETE.SeteEngine import SistemaSETE
from multiprocessing import Process, Pipe
import matplotlib.pyplot as plt
import pandas as pd
import shutil
import time
import os

import gc
gc.collect()

pd.set_option('display.precision',8) # SETANDO LIMIETE DE CASAS DECIMAIS PARA TRABALHO

time_out = 10
file_Start = "Start"
path_status = "Status\\"

def StartConection(user, password, codigo_cidade, conn):
    global time_out
    global file_Start
    global path_status

    while True:
        if file_Start in os.listdir(path_status): break
    time_start_req = time.time()
    sete = SistemaSETE(user, password)
    error = False
    while True:
        response1, conection1 = sete.AuthenticatorP()
        if conection1 is True:
            response2, conection2 = sete.AuthenticatorG()
            if conection2 is True and "result" in response2:
                if response2["result"] is True:
                    time_end = time.time()
                    break
        if (time.time() - time_start_req) >= time_out:
            error = True
            break
    if error is False:
        time_start = time.time()
        lista_alunos = sete.GetAlunos(codigo_cidade)
        time_end = time.time()
        time_current = time_end - time_start
    else:
        time_current = time_out
    conn.send(time_current)
    conn.close()

class TesteSete():

    def __init__(self):

        global time_out
        global file_Start
        global path_status

        self.path_datauser = "DataUsers\\"
        self.path_status = path_status # < FILE START
        self.path_save_testes = "DataUsersTeste\\" # FOLDER ID_PROCESS/TIMEPROCESS.TEXT
        self.template_teste = "Teste{}"
        self.file_Start = file_Start
        self.path_file_start_process = os.path.join(self.path_status, self.file_Start)
        self.time_out = time_out

        time_out = self.time_out
        file_Start = self.file_Start
        path_status = self.path_status

        self.id_process = 0
        self.user = ""
        self.password = ""
        self.InfoUsers = pd.DataFrame()
        self.CheckFolders()
        self.get_users()

    def InterFace(self):
        os.system("cls")
        self.users_available = len(self.InfoUsers.index) - self.id_process
        print(f" Existe {self.users_available} usuários disponíveis para teste.")
        while True:
            try:
                self.start_users =int(input(" Start Users?\n "))
                self.range_users =int(input(" Range Users?\n "))
                self.iterable_users =int(input(" N° Repetições ?\n "))
                break
            except:
                print(" Entradas com Erro, Digite Novamente!!")
                time.sleep(2)
                os.system("cls")
        # FUNÇÃO DE GERENCIAMENTO DE LOGIN QUE INICIALIZA OS MULTIPROCESS
        self.Management()
        print("Done!")
        self.ShowTeste()
        input(" Enter Para Reiniciar o Teste")
        self.InterFace()
    
    def CleanRestoration(self, path_folder):
        shutil.rmtree(path_folder, ignore_errors=True)
        try:
            os.mkdir(path_folder)
        except:
            pass

    def CheckFolders(self):
        if os.path.exists(self.path_datauser) is False:
            os.makedirs(self.path_datauser)
        if os.path.exists(self.path_save_testes) is False:
            os.makedirs(self.path_save_testes)
        self.CleanRestoration(self.path_status)

    def get_users(self):
        self.fileuser = os.listdir(self.path_datauser)[0]
        self.path_file_user = os.path.join(self.path_datauser, self.fileuser)
        self.InfoUsers = pd.read_csv(self.path_file_user, sep=",").reset_index(drop=True)
        return self.InfoUsers

    def TesteConection(self, user, codigo_cidade, password):
        time_start = time.time()
        sete = SistemaSETE(user, password)
        error = False
        while True:
            response1, conection1 = sete.AuthenticatorP()
            if conection1 is True:
                response2, conection2 = sete.AuthenticatorG()
                if conection2 is True and "result" in response2:
                    if response2["result"] is True:
                        time_end = time.time()
                        break
            if (time.time() - time_start) >= self.time_out:
                error = True
                break
        if error is False:
            time_current = time_end - time_start
            return time_current
        else:
            time_current = self.time_out
            return time_current

    def Management(self):

        self.list_range = [self.start_users]
        for _ in range(self.iterable_users):
            aux = self.list_range[-1] + self.range_users
            self.list_range.append(aux)
        
        input(f"Enter Para Iniciar o Teste.")
        
        self.list_DataFinal = []
        aux_espera_acumulativa = 0
        for teste in self.list_range:
            
            self.CheckFolders()
            self.df_final = pd.DataFrame()
            
            list_process = []
            list_vars = []
            for _ in range(1,teste+1):
                list_vars.append(Pipe())
                self.UserDAta = self.InfoUsers.iloc[self.id_process]
                user = self.UserDAta.email
                password = self.UserDAta.password
                codigo_cidade = self.UserDAta.codigo_cidade
                args=(
                    user, 
                    password,
                    codigo_cidade,
                    list_vars[-1][1],
                )
                p = Process(target=StartConection, args=args)
                gc.collect()
                list_process.append(p)
                p.start()
                print(f" Processo {self.id_process} Iniciado")
                self.id_process += 1

            print(f" Executando teste com {_} usuários.")
            espera_start = list(range(1,5+1+aux_espera_acumulativa))
            espera_start.reverse()
            for espera in espera_start:
                print(f"  * [Info] Iniciando em {espera}.")
                time.sleep(1)
            aux_espera_acumulativa+=1

            with open(self.path_file_start_process, "w") as file:
                print("\n DEU-SE A LARGADA!!.\n")

            while True:
                process = list_process[0]
                process.join()
                del(list_process[0])
                gc.collect()
                print("Processo Finalizado")
                if len(list_process) == 0: break
            del(process)
            gc.collect()
            print("\n")

            list_process = []
            list_time_process = []
            testesprocess = list(range(1, teste+1))
            testesprocess.reverse()
            itera = 0
            for parent_conn, child_conn in list_vars:
                list_process.append(testesprocess[itera])
                list_time_process.append(round(float(parent_conn.recv()),5))
                try:
                    child_conn.close()
                    del(child_conn)
                    gc.collect()
                except:
                    pass
                try:
                    del(parent_conn)
                    gc.collect()
                except:
                    pass
                itera+=1
            df_dict = {
                "Id Process": list_process,
                "Time Process": list_time_process
            }
            self.df_final = self.df_final.append(pd.DataFrame(df_dict))
            self.list_DataFinal.append(self.df_final)
            
            gc.collect()

        if len(os.listdir(self.path_save_testes)) == 0:
            self.template_teste = self.template_teste.format(1)
        else:
            list_id_all_testes = [int(row.split("Teste")[-1]) for row in os.listdir(self.path_save_testes)]
            list_id_all_testes = sorted(list_id_all_testes)
            id_teste = max(list_id_all_testes) + 1
            self.template_teste = self.template_teste.format(id_teste)
        
        self.folder_save_datateste = os.path.join(self.path_save_testes, self.template_teste)
        if os.path.exists(self.folder_save_datateste) is False:
            os.makedirs(self.folder_save_datateste)
        
        for self.save_df, id_teste_proces in zip(self.list_DataFinal, range(1, len(self.list_DataFinal))):
            
            self.save_df.to_csv(os.path.join(self.folder_save_datateste, f"Teste{id_teste_proces}.csv"), index=False, sep=";")

    def ShowTeste(self, show=True):
        self.all_x = []
        self.all_y = []
        for self.df_teste in self.list_DataFinal:
            x = len(self.df_teste["Id Process"])
            y = self.df_teste["Time Process"].mean()
            self.all_x.append(x)
            self.all_y.append(y)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.all_x, self.all_y)
        ax.set_title(f"Requests X Time [ST{self.start_users}-RA{self.range_users}-IT{self.iterable_users}]")
        ax.set_xlabel("Requisição em Paralelo")
        ax.set_ylabel("Tempo de Resposta")
        ax.figure.savefig(os.path.join(self.folder_save_datateste, f"BenchMark.png"))
        print("\n BenchMark SALVO!\n")
        if show is True:
            ax.figure.show()

if __name__ == '__main__':

    init = TesteSete()
    init.InterFace()