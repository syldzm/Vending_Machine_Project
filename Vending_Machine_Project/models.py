import json
import os
from datetime import datetime

class Drink:
    """음료 정보를 관리하기 위한 클래스"""
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock


class VendingMachine:
    """전체 자판기의 기능을 관리하는 클래스"""
    def __init__(self):
        # 17종 음료 초기 세팅
        self.drinks = {
            "아이시스": Drink("아이시스", 800, 0),         
            "더 킹": Drink("더 킹", 2000, 5),
            "레몬워터": Drink("레몬워터", 1800, 5),
            "옥수수수염차": Drink("옥수수수염차", 1600, 5),
            "트레비": Drink("트레비", 1300, 5),
            "펩시": Drink("펩시", 1100, 5),
            "칠성사이다": Drink("칠성사이다", 1300, 5),
            "망고": Drink("망고", 1200, 5),
            "립톤 아이스티": Drink("립톤 아이스티", 1200, 5),
            "사과 에이드": Drink("사과 에이드", 1100, 5),
            "포도 에이드": Drink("포도 에이드", 1100, 5),
            "비타파워": Drink("비타파워", 900, 5), 
            "코코팜 포도": Drink("코코팜 포도", 1000, 5),
            "핫식스": Drink("핫식스", 1300, 5),
            "레쓰비": Drink("레쓰비", 1200, 5),
            "게토레이": Drink("게토레이", 1000, 5),
            "잔치집 식혜": Drink("잔치집 식혜", 1000, 5)
        }
        self.current_money = 0      
        self.admin_password = "1707"  
        
        self.sales_history = {}     
        self.purchase_logs = []     
        self.changes_stock = {500: 10, 100: 20, 50: 20} 

        self.DATA_FILE = "vending_machine_data.json"
        self.load_data()

    def save_data(self):
        """현재 자판기의 모든 상태(음료, 잔돈, 매출역사, 로그)를 JSON으로 저장"""
        drinks_serialized = {
            name: {"price": drink.price, "stock": drink.stock}
            for name, drink in self.drinks.items()
        }
        save_dict = {
            "drinks": drinks_serialized,
            "changes_stock": self.changes_stock,
            "sales_history": self.sales_history,
            "purchase_logs": self.purchase_logs
        }
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, ensure_ascii=False, indent=4)

    def load_data(self):
        """저장된 JSON 파일이 있을 경우 데이터를 읽어와 복구"""
        if not os.path.exists(self.DATA_FILE):
            return
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data_dict = json.load(f)
            
            for name, info in data_dict.get("drinks", {}).items():
                self.drinks[name] = Drink(name, info["price"], info["stock"])
                
            self.changes_stock = {int(k): v for k, v in data_dict.get("changes_stock", {}).items()}
            self.sales_history = data_dict.get("sales_history", {})
            self.purchase_logs = data_dict.get("purchase_logs", {})
        except Exception as e:
            print(f"[데이터 로드 실패] 초기 상태로 기동합니다: {e}")

    def insert_money(self, money):
        """금액 입력 기능"""
        allowed_units = [1000, 500, 100, 50]
        if money in allowed_units:
            self.current_money += money
            if money in self.changes_stock:
                self.changes_stock[money] += 1
            self.save_data() 
            return True, f"{money}원이 투입되었습니다."
        else:
            return False, "[오류] 1000원, 500원, 100원, 50원 화폐만 입력 가능합니다."

    def check_purchase(self, drink_name):
        """선택한 음료의 구매 가능 여부를 판단하는 함수"""
        if drink_name not in self.drinks:
            return False, "존재하지 않는 음료입니다."
        
        drink = self.drinks[drink_name]
        if drink.stock <= 0:
            return False, f"'{drink_name}'은(는) 현재 재고가 없습니다. (품절)"
        if self.current_money < drink.price:
            missing = drink.price - self.current_money
            return False, f"금액이 부족합니다. ({missing}원 부족)"
            
        return True, "구매 가능합니다."

    def process_purchase(self, drink_name):
        """구매가 가능한 경우 실제 구매를 처리하는 함수"""
        is_available, message = self.check_purchase(drink_name)
        if not is_available:
            return False, message
            
        drink = self.drinks[drink_name]
        drink.stock -= 1                  
        self.current_money -= drink.price  
        
        self.sales_history[drink_name] = self.sales_history.get(drink_name, 0) + 1
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{now_str}] {drink_name} 구매 완료 (-{drink.price}원)"
        self.purchase_logs.append(log_entry)
        
        self.save_data() 
        return True, f"'{drink_name}'이(가) 나왔습니다."

    def calculate_change(self):
        """거스름돈 계산 및 반환 처리 함수"""
        if self.current_money == 0:
            return "반환할 거스름돈이 없습니다.", {}

        change_units = [500, 100, 50]
        temp_money = self.current_money
        giving_changes = {500: 0, 100: 0, 50: 0}

        for coin in change_units:
            count = temp_money // coin
            if count > 0:
                actual_count = min(count, self.changes_stock[coin])
                giving_changes[coin] = actual_count
                temp_money -= (coin * actual_count)

        if temp_money > 0:
            for coin, count in giving_changes.items():
                self.changes_stock[coin] -= count
            self.current_money = temp_money
            warning_msg = (
                "[거스름돈 부족 안내]\n"
                "자판기 내 잔돈 부족으로 인해 일부 거스름돈이 반환되지 못했습니다.\n"
                "지급된 잔돈 내역을 카메라로 기록하고, 관리자(010-XXXX-XXXX)에게로 연락해주세요."
            )
            self.save_data()
            return warning_msg, giving_changes
        else:
            for coin, count in giving_changes.items():
                self.changes_stock[coin] -= count
            success_msg = f"총 {self.current_money}원의 거스름돈이 정상 반환되었습니다."
            self.current_money = 0
            self.save_data()
            return success_msg, giving_changes

    def admin_login(self, input_pw):
        """관리자 모드에 접근하기 위한 인증 함수"""
        return self.admin_password == input_pw

    def update_drink_info(self, drink_name, new_price, new_stock):
        """기존 등록된 음료의 가격과 재고를 동시에 수정하는 함수"""
        if drink_name in self.drinks:
            self.drinks[drink_name].price = new_price
            self.drinks[drink_name].stock = new_stock
            self.save_data() 
            return f"[{drink_name}] 정보가 변경되었습니다. (가격: {new_price}원 / 재고: {new_stock}개)"
        else:
            return "[오류] 등록되지 않은 음료입니다."

    def add_new_drink(self, drink_name, price, stock):
        """새로운 음료만 단독 등록하는 전용 함수"""
        if drink_name in self.drinks:
            return f"[오류] '{drink_name}'은(는) 이미 자판기에 등록되어 있습니다."
        
        self.drinks[drink_name] = Drink(drink_name, price, stock)
        self.save_data() 
        return f"신규 음료 [{drink_name}]이(가) 자판기에 새롭게 입고되었습니다.\n(가격: {price}원 / 초기 재고: {stock}개)"

    def delete_drink(self, drink_name):
        """선택한 기존 음료를 자판기 메뉴에서 완전히 삭제하는 함수"""
        if drink_name in self.drinks:
            del self.drinks[drink_name]
            self.save_data() # 삭제 상태를 JSON 파일에 즉시 반영
            return f"[{drink_name}] 상품이 자판기 메뉴에서 완전히 삭제되었습니다."
        else:
            return "[오류] 존재하지 않거나 이미 삭제된 음료입니다."

    def manage_change(self, coin_unit, additional_count):
        """자판기 내부 잔돈(거스름돈 동전)을 충전하는 함수"""
        if coin_unit in self.changes_stock:
            self.changes_stock[coin_unit] += additional_count
            self.save_data() 
            return True, f"{coin_unit}원 동전이 {additional_count}개 추가되었습니다. (현재: {self.changes_stock[coin_unit]}개)"
        else:
            return False, "[오류] 올바른 동전 단위가 아닙니다. (500, 100, 50만 가능)"