import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
from models import VendingMachine

class VendingMachineGUI:
    def __init__(self, root):
        self.vm = VendingMachine()
        self.root = root
        self.root.title("2026150022 이환주 기말 프로젝트")
        self.root.geometry("480x750")
        self.root.configure(bg="#E8F5E9")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.drink_buttons = {}
        self.create_widgets()
        self.update_clock()

    def on_closing(self):
        """프로그램 종료 시 데이터를 최종 백업 후 메모리 해제"""
        self.vm.save_data()
        self.root.destroy()

    def create_widgets(self):
        # 상단 실시간 디지털 시계 배치
        self.clock_label = tk.Label(self.root, text="", font=("Courier", 11, "bold"), bg="#1B5E20", fg="#FFFFFF", pady=4)
        self.clock_label.pack(fill=tk.X, side=tk.TOP)

        # 타이틀 
        title = tk.Label(self.root, text="파이썬 자판기", font=("NanumGothic", 18, "bold"), bg="#E8F5E9", fg="#2E7D32")
        title.pack(pady=10)

        # 음료 종류 표시 프레임
        self.menu_frame = tk.LabelFrame(self.root, text=" 음료 목록 ", font=("NanumGothic", 11, "bold"), bg="#FFFFFF")
        self.menu_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
        self.update_drink_menu()

        # 잔액 표시
        self.money_label = tk.Label(self.root, text="현재 투입 금액: 0원", font=("NanumGothic", 14, "bold"), bg="#E8F5E9", fg="#1565C0")
        self.money_label.pack(pady=8)

        # 금액 입력 기능 버튼 그룹
        input_frame = tk.LabelFrame(self.root, text=" 금액 투입 ", bg="#E8F5E9")
        input_frame.pack(pady=5)
        
        units = [1000, 500, 100, 50]
        for unit in units:
            btn = tk.Button(input_frame, text=f"{unit}원", width=8, font=("NanumGothic", 10, "bold"),
                            command=lambda u=unit: self.click_insert_money(u), bg="#BBDEFB")
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 하단 제어부
        action_frame = tk.Frame(self.root, bg="#E8F5E9")
        action_frame.pack(pady=10, fill=tk.X, padx=20)

        change_btn = tk.Button(action_frame, text="거스름돈 반환", font=("NanumGothic", 11, "bold"), 
                               command=self.click_return_change, bg="#FFE082", height=2)
        change_btn.pack(fill=tk.X, side=tk.TOP, pady=2)

        admin_btn = tk.Button(action_frame, text="관리자 시스템 전환", font=("NanumGothic", 9), 
                              command=self.click_admin_mode, bg="#CFD8DC")
        admin_btn.pack(fill=tk.X, side=tk.TOP, pady=5)

    def update_clock(self):
        now_str = datetime.now().strftime("현재 시간 : %Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now_str)
        self.root.after(1000, self.update_clock)

    def update_drink_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for name, drink in self.vm.drinks.items():
            if drink.stock > 0:
                btn_text = f"{name}\n{drink.price}원\n(재고: {drink.stock}개)"
                btn_bg = "#E1F5FE"
                state_setting = tk.NORMAL
            else:
                btn_text = f"{name}\n{drink.price}원\n[품절]"
                btn_bg = "#FFCDD2"
                state_setting = tk.DISABLED

            btn = tk.Button(self.menu_frame, text=btn_text, font=("NanumGothic", 9), width=14, height=3,
                            bg=btn_bg, state=state_setting, command=lambda n=name: self.click_buy_drink(n))
            btn.grid(row=row, column=col, padx=8, pady=5)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

    def click_insert_money(self, amount):
        success, msg = self.vm.insert_money(amount)
        if success:
            self.money_label.config(text=f"현재 투입 금액: {self.vm.current_money}원")
        else:
            messagebox.showerror("입력 오류", msg)

    def click_buy_drink(self, name):
        success, msg = self.vm.process_purchase(name)
        if success:
            messagebox.showinfo("구매 성공", msg)
            self.money_label.config(text=f"현재 투입 금액: {self.vm.current_money}원")
            self.update_drink_menu()
        else:
            messagebox.showwarning("구매 실패", msg)

    def click_return_change(self):
        msg, details = self.vm.calculate_change()
        if details:
            detail_text = "\n\n[반환 동전 내역]\n" + "\n".join([f"- {k}원 동전: {v}개" for k, v in details.items() if v > 0])
            msg += detail_text
            
        messagebox.showinfo("거스름돈 반환", msg)
        self.money_label.config(text=f"현재 투입 금액: {self.vm.current_money}원")

    def click_admin_mode(self):
        pw = simpledialog.askstring("관리자 인증", "관리자 비밀번호를 입력하세요:", show='*')
        if pw is None: return
        if self.vm.admin_login(pw):
            self.open_admin_window()
        else:
            messagebox.showerror("인증 실패", "[오류] 비밀번호가 일치하지 않습니다.")

    def open_admin_window(self):
        admin_win = tk.Toplevel(self.root)
        admin_win.title("자판기 관리자 시스템")
        admin_win.geometry("450x530")
        admin_win.configure(bg="#ECEFF1")

        tk.Label(admin_win, text="자판기 관리자 모드", font=("NanumGothic", 14, "bold"), bg="#ECEFF1", fg="#37474F").pack(pady=10)

        notebook = ttk.Notebook(admin_win)
        notebook.pack(pady=5, padx=15, fill=tk.BOTH, expand=True)

        # 매출 현황 및 잔돈 재고
        tab1 = tk.Frame(notebook, bg="#FFFFFF")
        notebook.add(tab1, text=" 현황 및 잔돈 ")
        
        sales_text = tk.Text(tab1, font=("NanumGothic", 9), height=12)
        sales_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 시간별 상세 구매 로그 확인 창
        tab2 = tk.Frame(notebook, bg="#FFFFFF")
        notebook.add(tab2, text=" 실시간 구매 로그 ")
        
        log_text = tk.Text(tab2, font=("NanumGothic", 9), height=12, fg="#D32F2F")
        log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def refresh_admin_data():
            sales_text.delete('1.0', tk.END)
            sales_text.insert(tk.END, "[음료 총 판매 실적]\n")
            if not self.vm.sales_history:
                sales_text.insert(tk.END, "- 누적 판매 수량 없음\n")
            for name, count in self.vm.sales_history.items():
                # 삭제된 음료 예외처리 (딕셔너리에 없을 경우 기본값 출력)
                price = self.vm.drinks[name].price if name in self.vm.drinks else 0
                sales_text.insert(tk.END, f"- {name}: {count}개 판매 (금액: {price * count}원)\n")
            
            sales_text.insert(tk.END, "\n[자판기 보유 잔돈 현황]\n")
            for coin, count in self.vm.changes_stock.items():
                sales_text.insert(tk.END, f"- {coin}원 동전: {count}개\n")

            log_text.delete('1.0', tk.END)
            log_text.insert(tk.END, "[구매 시간 로그]\n")
            if not self.vm.purchase_logs:
                log_text.insert(tk.END, "- 기록된 구매 이벤트가 없습니다.\n")
            else:
                for log in reversed(self.vm.purchase_logs):
                    log_text.insert(tk.END, f"{log}\n")

        refresh_admin_data()

        # 하단 수정 기능 단추 그룹
        control_frame = tk.Frame(admin_win, bg="#ECEFF1")
        control_frame.pack(pady=10)

        def manage_existing_drink():
            if not self.vm.drinks:
                messagebox.showerror("오류", "등록된 음료수가 없습니다.", parent=admin_win)
                return

            edit_win = tk.Toplevel(admin_win)
            edit_win.title("기존 음료 정보 수정")
            edit_win.geometry("360x280")
            edit_win.configure(bg="#F5F5F5")
            edit_win.grab_set()

            tk.Label(edit_win, text="가격/재고 수정할 음료 선택", font=("NanumGothic", 10, "bold"), bg="#F5F5F5").pack(pady=5)
            drink_list = list(self.vm.drinks.keys())
            combo = ttk.Combobox(edit_win, values=drink_list, state="readonly", width=20, font=("NanumGothic", 10))
            combo.pack(pady=5)

            tk.Label(edit_win, text="새로운 가격 입력 (원)", font=("NanumGothic", 9), bg="#F5F5F5").pack(pady=2)
            price_entry = tk.Entry(edit_win, font=("NanumGothic", 10), justify='center', width=15)
            price_entry.pack(pady=2)

            tk.Label(edit_win, text="새로운 재고 수량 입력 (개)", font=("NanumGothic", 9), bg="#F5F5F5").pack(pady=2)
            stock_entry = tk.Entry(edit_win, font=("NanumGothic", 10), justify='center', width=15)
            stock_entry.pack(pady=2)

            def on_drink_select(event):
                selected_name = combo.get()
                if selected_name in self.vm.drinks:
                    drink_obj = self.vm.drinks[selected_name]
                    price_entry.delete(0, tk.END)
                    price_entry.insert(0, str(drink_obj.price))
                    stock_entry.delete(0, tk.END)
                    stock_entry.insert(0, str(drink_obj.stock))

            combo.bind("<<ComboboxSelected>>", on_drink_select)
            combo.current(0)
            on_drink_select(None) 

            # 수정 및 삭제 버튼을 나란히 배치하기 위한 서브 프레임 생성
            btn_frame = tk.Frame(edit_win, bg="#F5F5F5")
            btn_frame.pack(pady=15)

            def confirm_update():
                target_drink = combo.get()
                try:
                    p = int(price_entry.get())
                    s = int(stock_entry.get())
                    if p < 0 or s < 0: raise ValueError
                except ValueError:
                    messagebox.showerror("오류", "가격과 재고는 0 이상의 정수로 입력해야 합니다.", parent=edit_win)
                    return

                msg = self.vm.update_drink_info(target_drink, p, s)
                messagebox.showinfo("수정 완료", msg, parent=admin_win)
                edit_win.destroy()
                refresh_admin_data()
                self.update_drink_menu()

            def confirm_delete():
                target_drink = combo.get()
                if not target_drink: return
                
                # 경고 아이콘과 함께 사용자의 의사를 한 번 더 확인하는 내장 팝업
                answer = messagebox.askyesno(
                    "!경고!", 
                    f"정말로 자판기에서 [{target_drink}] 상품을 완전히 삭제하시겠습니까?", 
                    parent=edit_win
                )
                if answer: # Yes를 누른 경우에만 삭제 진행
                    msg = self.vm.delete_drink(target_drink)
                    messagebox.showinfo("삭제 완료", msg, parent=admin_win)
                    edit_win.destroy()
                    refresh_admin_data()
                    self.update_drink_menu()

            # 두 개의 기능 버튼을 좌우로 정렬 배치
            tk.Button(btn_frame, text="정보 변경 적용", command=confirm_update, bg="#B2DFDB", font=("NanumGothic", 10, "bold"), width=12).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="음료 삭제", command=confirm_delete, bg="#FFCDD2", fg="#C62828", font=("NanumGothic", 10, "bold"), width=12).pack(side=tk.LEFT, padx=5)

        def add_new_drink_window():
            add_win = tk.Toplevel(admin_win)
            add_win.title("신규 음료 추가")
            add_win.geometry("340x260")
            add_win.configure(bg="#F5F5F5")
            add_win.grab_set()

            tk.Label(add_win, text="신규 음료 이름 입력", font=("NanumGothic", 10, "bold"), bg="#F5F5F5").pack(pady=5)
            name_entry = tk.Entry(add_win, font=("NanumGothic", 10), justify='center', width=22)
            name_entry.pack(pady=2)
            name_entry.focus()

            tk.Label(add_win, text="판매 가격 설정 (원)", font=("NanumGothic", 9), bg="#F5F5F5").pack(pady=2)
            price_entry = tk.Entry(add_win, font=("NanumGothic", 10), justify='center', width=15)
            price_entry.pack(pady=2)

            tk.Label(add_win, text="최초 재고 수량 (개)", font=("NanumGothic", 9), bg="#F5F5F5").pack(pady=2)
            stock_entry = tk.Entry(add_win, font=("NanumGothic", 10), justify='center', width=15)
            stock_entry.pack(pady=2)

            def confirm_registration():
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("오류", "음료 이름을 입력해야 합니다.", parent=add_win)
                    return
                try:
                    p = int(price_entry.get())
                    s = int(stock_entry.get())
                    if p < 0 or s < 0: raise ValueError
                except ValueError:
                    messagebox.showerror("오류", "가격과 재고를 올바른 숫자로 입력해 주세요.", parent=add_win)
                    return

                msg = self.vm.add_new_drink(name, p, s)
                if "[오류]" in msg:
                    messagebox.showerror("등록 불가", msg, parent=add_win)
                else:
                    messagebox.showinfo("등록 완료", msg, parent=admin_win)
                    add_win.destroy()
                    refresh_admin_data()
                    self.update_drink_menu()

            tk.Button(add_win, text="새 음료 자판기 배치", command=confirm_registration, bg="#FFE082", font=("NanumGothic", 10, "bold")).pack(pady=12)

        def refill_change():
            coin = simpledialog.askinteger("잔돈 충전", "충전할 동전 단위를 입력하세요 (500, 100, 50)", parent=admin_win)
            if coin is None: return
            if coin not in [500, 100, 50]:
                messagebox.showerror("오류", "[오류] 500, 100, 50원 단위만 충전할 수 있습니다.", parent=admin_win)
                return
            
            count = simpledialog.askinteger("잔돈 충전", f"{coin}원 동전을 추가할 개수를 입력하세요:", parent=admin_win, minvalue=1)
            if count is None: return
            
            success, msg = self.vm.manage_change(coin, count)
            if success:
                messagebox.showinfo("충전 완료", msg, parent=admin_win)
                refresh_admin_data()
            else:
                messagebox.showerror("오류", msg, parent=admin_win)
        
        tk.Button(control_frame, text="기존 음료 관리", width=28, command=manage_existing_drink, bg="#B2DFDB").pack(pady=3)
        tk.Button(control_frame, text="신규 음료 추가", width=28, command=add_new_drink_window, bg="#FFE082").pack(pady=3)
        tk.Button(control_frame, text="잔돈 충전", width=28, command=refill_change, bg="#A5D6A7").pack(pady=3)
        tk.Button(admin_win, text="닫기", command=admin_win.destroy, bg="#B0BEC5").pack(pady=5)