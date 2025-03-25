import tkinter as tk
from tkinter import filedialog, ttk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
# Matplotlib 버전에 따라 적절한 import 사용
try:
    # 최신 버전 Matplotlib (>=3.6)
    from matplotlib import colormaps
    def get_cmap(name):
        return colormaps[name]
except ImportError:
    try:
        # 중간 버전 Matplotlib
        from matplotlib.pyplot import get_cmap
    except ImportError:
        # 구 버전 Matplotlib
        from matplotlib.cm import get_cmap

class DepthDoseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Line-dose (range & SOBP)")
        self.root.geometry("900x600")
        
        self.selected_files = []
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        
        # 데이터 저장 변수
        self.depth_data = {}  # 키: 파일명, 값: depth 배열
        self.dose_data = {}   # 키: 파일명, 값: dose 배열
        self.file_types = {}  # 키: 파일명, 값: 'plan' 또는 'measurement'
        
        # 메인 프레임 생성
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 버튼 프레임
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # 버튼 스타일 설정 함수
        def on_enter(e, button):
            button.config(background='#E0E0FF')  # 마우스 오버 색상
            
        def on_leave(e, button):
            button.config(background='SystemButtonFace')  # 기본 색상으로 복원            
        
        # Open Files 버튼 (외곽선 제거)
        self.open_button = tk.Button(self.button_frame, text="Open\nfiles", 
                                    command=self.open_files, width=8, height=2,
                                    relief=tk.RIDGE, bd=2)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 마우스 오버 이벤트 연결
        self.open_button.bind("<Enter>", lambda e: on_enter(e, self.open_button))
        self.open_button.bind("<Leave>", lambda e: on_leave(e, self.open_button))
        
        # Save Screen 버튼 (외곽선 제거)
        self.save_screen_button = tk.Button(self.button_frame, text="Save\nscreen", 
                                        command=self.save_full_screen, width=8, height=2,
                                        relief=tk.RIDGE, bd=2)
        self.save_screen_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 마우스 오버 이벤트 연결
        self.save_screen_button.bind("<Enter>", lambda e: on_enter(e, self.save_screen_button))
        self.save_screen_button.bind("<Leave>", lambda e: on_leave(e, self.save_screen_button))
        
        # 콘텐츠 프레임
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 그래프 프레임 (왼쪽, 비율 70%)
        self.graph_frame = tk.LabelFrame(self.content_frame, text="Depth-dose curves")
        self.graph_frame.place(relx=0, rely=0, relwidth=0.7, relheight=1.0)
                
        # 그래프 초기화
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 파일 정보 프레임 (오른쪽, 비율 30%)
        self.info_frame = tk.LabelFrame(self.content_frame, text="Range & SOBP")
        self.info_frame.place(relx=0.7, rely=0, relwidth=0.3, relheight=1.0)
        
        # 스타일 설정 - 얇은 테두리 표시
        style = ttk.Style()
        style.configure("Treeview", 
                      rowheight=25,  # 행 높이
                      borderwidth=1)  # 테두리 두께
        style.configure("Treeview.Heading", 
                      font=('TkDefaultFont', 9, 'bold'),  # 헤더 폰트
                      borderwidth=1)  # 헤더 테두리 두께
                      
        # 셀 테두리 표시를 위한 스타일
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe', 'border': '1'})
        ])
        
        # 트리뷰 생성 및 스크롤바 추가
        self.info_frame_inner = tk.Frame(self.info_frame)
        self.info_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 수직 스크롤바
        scrollbar_y = ttk.Scrollbar(self.info_frame_inner, orient="vertical")
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 수평 스크롤바
        scrollbar_x = ttk.Scrollbar(self.info_frame_inner, orient="horizontal")
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 파일 정보 표시 트리뷰 - 열 너비 자동 조정
        self.info_tree = ttk.Treeview(self.info_frame_inner, 
                                     columns=("param", "plan", "measured"), 
                                     show="headings",
                                     yscrollcommand=scrollbar_y.set,
                                     xscrollcommand=scrollbar_x.set)
        
        # 스크롤바 연결
        scrollbar_y.config(command=self.info_tree.yview)
        scrollbar_x.config(command=self.info_tree.xview)
        
        # 클립보드 복사 기능 추가
        self.info_tree.bind('<Control-c>', self.copy_selection)
        # 마우스 우클릭 메뉴 추가
        self.info_tree.bind('<Button-3>', self.show_context_menu)
        
        # 컬럼 설정
        self.info_tree.heading("param", text="Values")
        self.info_tree.heading("plan", text="Plan")
        self.info_tree.heading("measured", text="Measured")
        
        # 컬럼 너비 설정
        self.info_tree.column("param", width=100, minwidth=80)
        self.info_tree.column("plan", width=70, minwidth=50)
        self.info_tree.column("measured", width=70, minwidth=50)
        
        # 그리드 활성화 (행/열 구분선 표시)
        self.info_tree.tag_configure('evenrow', background='#f0f0f0')
        self.info_tree.tag_configure('oddrow', background='#ffffff')
        
        self.info_tree.pack(fill=tk.BOTH, expand=True)
        
        # 초기 샘플 데이터 추가
        self.info_tree.insert("", tk.END, values=("", "", ""), tags=('evenrow',))
        self.info_tree.insert("", tk.END, values=("D90", "", ""), tags=('oddrow',))
        self.info_tree.insert("", tk.END, values=("D95", "", ""), tags=('evenrow',))
        self.info_tree.insert("", tk.END, values=("SOBP", "", ""), tags=('oddrow',))
        self.info_tree.insert("", tk.END, values=("D20", "", ""), tags=('evenrow',))
        self.info_tree.insert("", tk.END, values=("D10", "", ""), tags=('oddrow',))
    
    
    def save_full_screen(self):
        """전체 화면 저장 기능"""
        if not self.selected_files:
            tk.messagebox.showinfo("알림", "저장할 화면이 없습니다. 먼저 파일을 열어주세요.")
            return
        
        file_path = filedialog.asksaveasfilename(
            initialdir=self.current_directory,
            title="전체 화면 저장",
            filetypes=(("PNG 파일", "*.png"), ("모든 파일", "*.*")),
            defaultextension=".png"
        )
        
        if file_path:
            try:
                # 1. PIL 라이브러리 사용 방식
                from PIL import ImageGrab
                
                # 현재 창의 위치와 크기 가져오기
                x = self.root.winfo_rootx()
                y = self.root.winfo_rooty()
                width = self.root.winfo_width()
                height = self.root.winfo_height()
                
                # 화면 캡처
                screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
                screenshot.save(file_path)
                
                # 성공 메시지
                tk.messagebox.showinfo("성공", f"전체 화면이 저장되었습니다.\n{file_path}")
            except Exception as e:
                tk.messagebox.showerror("오류", f"화면 저장 중 오류가 발생했습니다.\n{e}") 
            
    def open_files(self):
        """파일 열기 다이얼로그를 실행하고 선택된 파일들을 처리"""
        file_paths = filedialog.askopenfilenames(
            initialdir = self.current_directory,
            title="파일 선택",
            filetypes=(("Data files", "*.txt;*.csv"), ("All files", "*.*"))
        )
        
        if file_paths:
            self.selected_files = list(file_paths)
            self.extract_data()
            print("extract OK")
            self.plot_depth_dose_curves()
            print("draw dd curve")
            self.update_file_info()
            
    def extract_data(self):
        """파일에서 데이터를 추출하여 depth와 dose 변수에 저장"""
        # 데이터 저장소 초기화
        self.depth_data = {}
        self.dose_data = {}
        self.file_types = {}
        
        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            ext = os.path.splitext(file_path)[1].lower()
            
            try:
                # 확장자에 따라 다른 데이터 추출 함수 사용
                if ext == '.csv':
                    depth, dose = self.extract_csv_data(file_path)
                    self.file_types[file_name] = 'measurement'
                elif ext == '.txt':
                    depth, dose = self.extract_txt_data(file_path)
                    self.file_types[file_name] = 'plan'
                else:
                    raise ValueError(f"지원되지 않는 파일 형식: {ext}")
                
                # 데이터 정규화 (최대값을 100으로)
                dose = (np.array(dose) / np.max(dose)) * 100
                
                tmp_d90_ind = np.where(dose >= 90 )[0]
                tmp_d90_depth = depth[tmp_d90_ind.max()] if tmp_d90_ind.size > 0 else 0
                
                tmp_p95_ind = np.where(dose >= 95 )[0]
                tmp_p95_depth = depth[tmp_p95_ind.min()] if tmp_p95_ind.size > 0 else 0
                
                mid_sobp_index = int((tmp_d90_ind.max() + tmp_p95_ind.min())/2)
                
                # 추출된 데이터 저장
                self.depth_data[file_name] = depth
                self.dose_data[file_name] = 100*dose/np.mean(dose[mid_sobp_index-1:mid_sobp_index+1])

                
                print(f"파일 '{file_name}' 데이터 추출 완료 ({self.file_types[file_name]})")
                
            except Exception as e:
                print(f"파일 '{file_name}' 데이터 추출 오류: {e}")
    
    def extract_csv_data(self, csv_file):
        """CSV 파일에서 깊이와 선량 데이터 추출"""
        depth = []
        dose = []
        with open(csv_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
    
        reading_depth = False
        reading_dose = False
    
        for line in lines:
            line = line.strip()
    
            if "Curve depth: [mm]" in line:
                reading_depth = True
                reading_dose = False
                continue
    
            if "Curve gains: [counts]" in line:
                reading_dose = True
                reading_depth = False
                continue
    
            if reading_depth and line:
                depth.extend(map(float, line.split(";")))
    
            if reading_dose and line:
                dose.extend(map(float, line.split(";")))
    
            if reading_dose and line == "":
                break
    
        return depth, dose
    
    def extract_txt_data(self, txt_file):
        """TXT 파일에서 깊이와 선량 데이터 추출"""
        depth = []
        dose = []
        reading_data = False
    
        with open(txt_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
    
        for line in lines:
            line = line.strip()
    
            if "Distance(cm)   Dose (cGy)" in line:
                reading_data = True
                continue
    
            if reading_data:
                parts = line.split()
                if len(parts) == 2:
                    # cm to mm 변환
                    depth.append(float(parts[0]) * 10)
                    dose.append(float(parts[1]))
    
        return depth, dose
    
    def plot_depth_dose_curves(self):
        """깊이-선량 곡선 그래프 생성"""
        self.ax.clear()
        
        if not self.selected_files:
            self.canvas.draw()
            return
        
        # 색상 맵 설정 (다중 파일 구분을 위한 색상)
        colormap = get_cmap('tab10')
        colors = [colormap(i % 10) for i in range(len(self.selected_files))]
        
        # 파일별 그래프 플로팅
        for i, file_name in enumerate(self.depth_data.keys()):
            depth = self.depth_data[file_name]
            dose = self.dose_data[file_name]
            file_type = self.file_types[file_name]
            
            # 파일 유형에 따라 라인 스타일 다르게 설정
            if file_type == 'plan':
                linestyle = '-'
            else:  # measurement
                linestyle = '--'
            
            self.ax.plot(depth, dose, label=file_name, color=colors[i], linestyle=linestyle)
        
        self.ax.set_xlabel('depth (mm)')
        self.ax.set_ylabel('dose (%)')
        self.ax.grid(True)
        self.ax.legend()
        
        # x축 범위를 0-300mm로 제한
        self.ax.set_xlim(0, 300)
        
        self.canvas.draw()
        
    def find_x_for_y(self, x_values, y_values, target_y):
        """
        주어진 x와 y 데이터에서 목표 y값에 해당하는 x값을 내삽법으로 찾는 함수
        numpy.interp만 사용하여 구현
        
        Parameters:
        x_values (list/array): x 좌표값 리스트
        y_values (list/array): y 좌표값 리스트
        target_y (float): 찾고자 하는 y 값
        
        Returns:
        float: 목표 y값에 해당하는 x값
        """
        # y값으로 x값을 찾아야 하므로 x와 y를 반대로 입력
        # numpy.interp는 오름차순 데이터를 요구하므로 정렬 필요
        
        # 만약 target_y가 y_values의 범위를 벗어나면 예외 처리
        if target_y < min(y_values) or target_y > max(y_values):
            raise ValueError(f"목표값 {target_y}가 데이터 범위({min(y_values)}-{max(y_values)}) 밖에 있습니다.")
        
        # y 기준으로 정렬 (오름차순)
        sorted_indices = np.argsort(y_values)
        sorted_y = np.array(y_values)[sorted_indices]
        sorted_x = np.array(x_values)[sorted_indices]
        
        # numpy.interp를 사용하여 x값 계산 (x와 y 역할 바꿈)
        target_x = float(np.interp(target_y, sorted_y, sorted_x))
        
        return target_x        
        
        
    def update_file_info(self):
        """파일 정보 표시 업데이트"""
        # 기존 항목 지우기
        for item in self.info_tree.get_children():
            self.info_tree.delete(item)
        
        # 선택된 파일들에 대한 정보 저장
        plan_depth_values = {}
        measured_depth_values = {}
        
        for file_name in self.depth_data.keys():
            depth = self.depth_data[file_name]
            dose = self.dose_data[file_name]
            file_type = self.file_types[file_name]
            
            try:
                # 선량 지표 계산
                # max_dose = 100  # 이미 정규화되어 있음
                
                # D90 (90% 선량 깊이)
                d90_indices = np.where(dose >= 90)[0]
                d90_maxind = d90_indices.max()
                    
                if d90_indices.size > 0:                    
                    d90_depth = self.find_x_for_y(depth[d90_maxind:d90_maxind + 3],
                                                  dose[d90_maxind:d90_maxind + 3], 90)                 
                else: 0
                                
                # D50 (50% 선량 깊이)
                d50_indices = np.where(dose >= 50)[0]
                if d50_indices.size > 0:                    
                    d50_depth = self.find_x_for_y(depth[d50_indices.max():d50_indices.max()+3],
                                                  dose[d50_indices.max():d50_indices.max()+3], 50)                 
                else: 0
                
                # D20 (20% 선량 깊이)
                d20_indices = np.where(dose >= 20)[0]
                if d20_indices.size > 0:                    
                    d20_depth = self.find_x_for_y(depth[d20_indices.max():d20_indices.max()+3],
                                                  dose[d20_indices.max():d20_indices.max()+3], 20)                 
                else: 0
                
                # D10 (10% 선량 깊이)
                d10_indices = np.where(dose >= 10)[0]
                if d10_indices.size > 0:                    
                    d10_depth = self.find_x_for_y(depth[d10_indices.max():d10_indices.max()+3],
                                                  dose[d10_indices.max():d10_indices.max()+3], 10)                 
                else: 0                
                                
                # P95 (95% proximal 선량 깊이)
                p95_indices = np.where(dose >= 95)[0]
                if p95_indices.size > 0:                    
                    p95_depth = self.find_x_for_y(depth[p95_indices.min()-2:p95_indices.min()+1],
                                                  dose[p95_indices.min()-2:p95_indices.min()+1], 95)                 
                else: 0
                
                # SOBP                                
                sobp_width = d90_depth - p95_depth
                
                # 파일 유형에 따라 값 저장
                if file_type == 'plan':
                    plan_depth_values = {
                        'file': file_name,
                        'D90': f"{d90_depth:.2f} mm",
                        'SOBP': f"{sobp_width:.2f} mm",
                        'D50': f"{d50_depth:.2f} mm",
                        'D20': f"{d20_depth:.2f} mm",
                        'D10': f"{d10_depth:.2f} mm"
                    }
                else:  # measurement
                    measured_depth_values = {
                        'file': file_name,
                        'D90': f"{d90_depth:.2f} mm",
                        'SOBP': f"{sobp_width:.2f} mm",
                        'D50': f"{d50_depth:.2f} mm",
                        'D20': f"{d20_depth:.2f} mm",
                        'D10': f"{d10_depth:.2f} mm"
                    }
            
            except Exception as e:
                print(f"파일 분석 오류 ({file_name}): {e}")
        
        # 계산된 값들을 테이블에 추가
        row_count = 0
        depth_params = ['file', 'D90', 'SOBP', 'D50', 'D20', 'D10']
        
        for param in depth_params:
            row_tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            row_count += 1
            
            plan_value = plan_depth_values.get(param, '')
            measured_value = measured_depth_values.get(param, '')
            
            self.info_tree.insert("", tk.END, 
                values=(param, plan_value, measured_value), 
                tags=(row_tag,))
        
        # 테이블 값에 따라 열 너비 자동 조정
        self.adjust_column_widths()      
        
    def adjust_column_widths(self):
        """테이블 컬럼 너비 자동 조정"""
        for column in ("param", "plan", "measured"):
            # 헤더 텍스트 길이
            header_width = len(self.info_tree.heading(column)['text']) * 10
            
            # 모든 행에서 해당 열의 값 길이 확인
            max_width = header_width
            for item in self.info_tree.get_children():
                cell_value = str(self.info_tree.set(item, column))
                cell_width = len(cell_value) * 8  # 픽셀 단위 대략적인 계산
                max_width = max(max_width, cell_width)
            
            # 최소 너비 설정 및 20% 여유 공간 추가
            min_width = 50
            column_width = max(min_width, int(max_width * 1.2))
            
            # 열 너비 설정
            self.info_tree.column(column, width=column_width, minwidth=min_width)
    
    def save_figure(self):
        """그래프 저장"""
        if not self.selected_files:
            tk.messagebox.showinfo("알림", "저장할 그래프가 없습니다. 먼저 파일을 열어주세요.")
            return
        
        file_path = filedialog.asksaveasfilename(
            initialdir=self.current_directory,
            title="그래프 저장",
            filetypes=(("PNG 파일", "*.png"), ("PDF 파일", "*.pdf"), ("모든 파일", "*.*")),
            defaultextension=".png"
        )
        
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                tk.messagebox.showinfo("성공", f"그래프가 저장되었습니다.\n{file_path}")
            except Exception as e:
                tk.messagebox.showerror("오류", f"그래프 저장 중 오류가 발생했습니다.\n{e}")
    
    # 데이터 추출 함수를 위한 공간 (향후 추가할 예정)
    def get_extracted_data(self):
        """추출된 데이터 반환 (depth와 dose)"""
        return self.depth_data, self.dose_data, self.file_types
    
    def copy_selection(self, event=None):
        """선택된 항목을 클립보드에 복사"""
        # 선택된 항목 가져오기
        selected_items = self.info_tree.selection()
        
        if not selected_items:
            return
            
        # 클립보드에 복사할 텍스트 준비
        copy_text = ""
        
        # 선택된 각 행의 값을 탭으로 구분하여 추가
        for item in selected_items:
            values = self.info_tree.item(item, 'values')
            row_text = "\t".join([str(val) for val in values])
            copy_text += row_text + "\n"
            
        # 클립보드에 복사
        self.root.clipboard_clear()
        self.root.clipboard_append(copy_text)
        self.root.update()  # 클립보드 업데이트 적용
        
        # 상태 메시지 (옵션)
        print(f"{len(selected_items)}개 항목이 클립보드에 복사됨")
    
    def show_context_menu(self, event):
        """마우스 우클릭 시 컨텍스트 메뉴 표시"""
        # 마우스 위치의 항목 선택
        item = self.info_tree.identify_row(event.y)
        if item:
            # 이미 선택된 항목 유지하면서 추가 선택
            if item not in self.info_tree.selection():
                self.info_tree.selection_set(item)
        
        # 선택된 항목이 있는 경우에만 메뉴 표시
        if self.info_tree.selection():
            # 컨텍스트 메뉴 생성
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="복사", command=self.copy_selection)
            
            # 마우스 위치에 메뉴 표시
            context_menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = DepthDoseGUI(root)
    root.mainloop()