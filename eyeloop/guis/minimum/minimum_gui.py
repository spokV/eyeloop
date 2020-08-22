import os
from pathlib import Path

import numpy as np
import eyeloop.config as config

from eyeloop.constants.minimum_gui_constants import *
from eyeloop.utilities.general_operations import to_int, tuple_int

import pickle
import io
import socket
import struct
import time
import zlib

class GUI:
    def __init__(self) -> None:

        dir_path = os.path.dirname(os.path.realpath(__file__))
        tool_tip_dict = ["tip_1_cr", "tip_2_cr", "tip_3_pupil", "tip_4_pupil", "tip_5_start", "tip_1_cr_error", "",
                         "tip_3_pupil_error"]
        self.first_tool_tip = cv2.imread("{}/graphics/{}.png".format(dir_path, "tip_1_cr_first"), 0)
        self.tool_tips = [cv2.imread("{}/graphics/{}.png".format(dir_path, tip), 0) for tip in tool_tip_dict]

        self._state = "adjustment"
        self.inquiry = "none"
        self.terminate = -1

        self.gui_data = b""
        self.gui_data_payload_size = struct.calcsize(">iii")

        print("Connecting to gui server\n")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.1.196', 8485))
        self.connection = self.client_socket.makefile('wb')
        self.client_socket.settimeout(0.2)
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def send_frame_with_context(self, frame_np, context):
        result, frame = cv2.imencode('.jpg', frame_np, self.encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)
        try:
            self.client_socket.sendall(struct.pack(">LI", size, context) + data)
        except socket.timeout:
            pass

    def tip_mousecallback(self, event, x: int, y: int, flags, params) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            if 10 < y < 35:
                if 20 < x < 209:
                    x -= 27
                    x = int(x / 36) + 1

                    self.update_tool_tip(x)

    def mousecallback(self, event, x, y, flags, params) -> None:
        x = x % self.width
        self.cursor = (x, y)

    def release(self):
        self.out.release()
        cv2.destroyAllWindows()

    def remove_mousecallback(self) -> None:
        cv2.setMouseCallback("CONFIGURATION", lambda *args: None)
        cv2.setMouseCallback("Tool tip", lambda *args: None)

    def update_tool_tip(self, index: int, error: bool = False) -> None:
        if error:
            #cv2.imshow("Tool tip", self.tool_tips[index + 4])
            self.send_frame_with_context(self.tool_tips[index + 4], 4)
        else:
            #cv2.imshow("Tool tip", self.tool_tips[index - 1])
            self.send_frame_with_context(self.tool_tips[index - 1], 4)

    def key_listener(self, key: int) -> None:
        try:
            key = chr(key)
        except:
            return

        if self.inquiry == "track":
            if "y" == key:
                print("Initiating tracking..")
                #self.remove_mousecallback()
                
                #cv2.destroyWindow("CONFIGURATION")
                #cv2.destroyWindow("BINARY")
                #cv2.destroyWindow("Tool tip")

                #cv2.imshow("TRACKING", self.PStock)
                #cv2.moveWindow("TRACKING", 100, 100)
                self.send_frame_with_context(self.PStock, 2)

                self._state = "tracking"
                self.inquiry = "none"

                config.engine.activate()

                return
            elif "n" == key:
                print("Adjustments resumed.")
                self._state = "adjustment"
                self.inquiry = "none"
                return

        if self._state == "adjustment":
            if key == "p":
                config.engine.angle -= 5

            elif key == "o":
                config.engine.angle += 5

            elif key == "b":

                config.engine.marks.append(self.cursor)

            elif key == "v":
                try:
                    config.engine.marks.pop()
                except:
                    # empty list
                    pass

            elif "1" == key:
                try:
                    config.engine.pupil = self.cursor
                    self.pupil_processor.reset(self.cursor, np.mean(
                        config.engine.source[self.cursor[1] - 1:self.cursor[1] + 1,
                        self.cursor[0] - 1:self.cursor[0] + 1]))

                    config.engine.refresh_pupil = self.pupil_processor.refresh_source
                    # self.pupil_processor.track()
                    self.update_tool_tip(4)

                    print("\nPupil selected.")
                    print("Adjust binarization via R/F (threshold) and T/G (smoothing).")
                except Exception as e:
                    print(e)
                    self.update_tool_tip(3, True)
                    print("Try again: Hover and click on the pupil, then press 1.")

            elif "2" == key:
                try:

                    self.current_cr_processor = config.engine.cr_processors[0]

                    self.current_cr_processor.reset(self.cursor, np.mean(
                        config.engine.source[self.cursor[1] - 1:self.cursor[1] + 1,
                        self.cursor[0] - 1:self.cursor[0] + 1]))

                    self.update_tool_tip(2)

                    print("\nCorneal reflex selected.")
                    print("Adjust binarization via W/S (threshold) and E/D (smoothing).")

                except:
                    self.update_tool_tip(1, True)
                    print("Hover and click on the corneal reflex, then press 2.")

            elif "3" == key:
                try:
                    self.update_tool_tip(2)
                    self.current_cr_processor = config.engine.cr_processors[1]

                    self.current_cr_processor.reset(self.cursor, np.mean(
                        config.engine.source[self.cursor[1] - 1:self.cursor[1] + 1,
                        self.cursor[0] - 1:self.cursor[0] + 1]))

                    print("\nCorneal reflex selected.")
                    print("Adjust binarization via W/S (threshold) and E/D (smoothing).")

                except:
                    self.update_tool_tip(1, True)
                    print("Hover and click on the corneal reflex, then press 3.")

            elif "4" == key:
                try:
                    self.update_tool_tip(2)
                    self.current_cr_processor = config.engine.cr_processors[2]

                    self.current_cr_processor.reset(self.cursor, np.mean(
                        config.engine.source[self.cursor[1] - 1:self.cursor[1] + 1,
                        self.cursor[0] - 1:self.cursor[0] + 1]))

                    print("\nCorneal reflex selected.")
                    print("Adjust binarization via W/S (threshold) and E/D (smoothing).")

                except:
                    self.update_tool_tip(1, True)
                    print("Hover and click on the corneal reflex, then press 4.")

            elif "z" == key:
                print("Start tracking? (y/n)")
                self.inquiry = "track"
                self.client_socket.settimeout(0.001)

            elif "w" == key:

                self.current_cr_processor.binarythreshold += 1
                # print("Corneal reflex binarization threshold increased (%s)." % self.CRProcessor.binarythreshold)

            elif "s" == key:

                self.current_cr_processor.binarythreshold -= 1
                # print("Corneal reflex binarization threshold decreased (%s)." % self.CRProcessor.binarythreshold)

            elif "e" == key:

                self.current_cr_processor.blur += 2
                # print("Corneal reflex blurring increased (%s)." % self.CRProcessor.blur)

            elif "d" == key:

                self.current_cr_processor.blur -= 2
                # print("Corneal reflex blurring decreased (%s)." % self.CRProcessor.blur)

            elif "r" == key:
                self.pupil_processor.binarythreshold += 1
                # print("Pupil binarization threshold increased (%s)." % self.pupil_processor.binarythreshold)
            elif "f" == key:
                self.pupil_processor.binarythreshold -= 1
                # print("Pupil binarization threshold decreased (%s)." % self.pupil_processor.binarythreshold)

            elif "t" == key:

                self.pupil_processor.blur += 2
                # print("Pupil blurring increased (%s)." % self.pupil_processor.blur)

            elif "g" == key:

                self.pupil_processor.blur -= 2
                # print("Pupil blurring decreased (%s)." % self.pupil_processor.blur)

        if "q" == key:
            # Terminate tracking
            config.engine.release()

    def arm(self, width: int, height: int) -> None:

        self.pupil_processor = config.engine.pupil_processor

        self.cr_index = 0
        self.current_cr_processor = config.engine.cr_processors[0]  # primary corneal reflection

        if config.arguments.markers == False:
            self.place_markers = lambda: None
        else:
            self.place_markers = self.rplace_markers

        self.width, self.height = width, height
        self.binary_width = max(width, 300)
        self.binary_height = max(height, 200)

        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        output_vid = Path(config.file_manager.new_folderpath, "output.avi")
        self.out = cv2.VideoWriter(str(output_vid), fourcc, 50.0, (self.width, self.height))

        self.PStock = np.zeros((self.binary_height, self.binary_width))
        self.CRStock = self.PStock.copy()

        self.src_txt = np.zeros((20, width, 3))
        self.prev_txt = self.src_txt.copy()
        cv2.putText(self.src_txt, 'Source', (15, 12), font, .7, (255, 255, 255), 0, cv2.LINE_4)
        cv2.putText(self.prev_txt, 'Preview', (15, 12), font, .7, (255, 255, 255), 0, cv2.LINE_4)
        cv2.putText(self.prev_txt, 'EyeLoop', (width - 50, 12), font, .5, (255, 255, 255), 0, cv2.LINE_8)

        self.pstock_txt = np.zeros((20, self.binary_width))
        self.pstock_txt_selected = self.pstock_txt.copy()
        self.crstock_txt = self.pstock_txt.copy()
        self.crstock_txt[0:1, 0:self.binary_width] = 1
        self.crstock_txt_selected = self.crstock_txt.copy()

        cv2.putText(self.pstock_txt, 'P | R/F | T/G || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)
        cv2.putText(self.pstock_txt_selected, '(*) P | R/F | T/G || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)

        cv2.putText(self.crstock_txt, 'CR | W/S | E/D || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)
        cv2.putText(self.crstock_txt_selected, '(*) CR | W/S | E/D || bin/blur', (10, 15), font, .7, 1, 0, cv2.LINE_4)

        #cv2.imshow("CONFIGURATION", np.hstack((self.PStock, self.PStock)))
        self.send_frame_with_context(np.hstack((self.PStock, self.PStock)), 0)
        #cv2.imshow("BINARY", np.vstack((self.PStock, self.PStock)))
        self.send_frame_with_context(np.vstack((self.PStock, self.PStock)), 1)

        #cv2.moveWindow("BINARY", 105 + width * 2, 100)
        #cv2.moveWindow("CONFIGURATION", 100, 100)

        #cv2.imshow("Tool tip", self.first_tool_tip)
        self.send_frame_with_context(self.first_tool_tip, 4)

        #cv2.moveWindow("Tool tip", 100, 100 + height + 100)
        #try:
        #    cv2.setMouseCallback("CONFIGURATION", self.mousecallback)
        #    cv2.setMouseCallback("Tool tip", self.tip_mousecallback)
        #except:
        #    print("Could not bind mouse-buttons.")

    def place_cross(self, source: np.ndarray, point: tuple, color: tuple) -> None:
        try:
            source[to_int(point[1] - 3):to_int(point[1] + 4), to_int(point[0])] = color
            source[to_int(point[1]), to_int(point[0] - 3):to_int(point[0] + 4)] = color
        except:
            pass

    def rplace_markers(self, source: np.ndarray) -> None:
        for i, mark in enumerate(config.engine.marks):
            self.place_cross(source, mark, blue)
            if (i % 2) == 0:
                try:
                    self.place_cross(source, config.engine.marks[i + 1], pink)
                    cv2.rectangle(source, mark, config.engine.marks[i + 1], blue)
                except:
                    # odd number of marks
                    break

    def update_record(self, frame_preview) -> None:
        #cv2.imshow("Recording", frame_preview)
        self.send_frame_with_context(frame_preview, 3)
        if cv2.waitKey(1) == ord('q'):
            config.engine.release()

    def update_track(self, blink: int) -> None:
        frame_preview = cv2.cvtColor(config.engine.source, cv2.COLOR_GRAY2BGR)
        frame_source = frame_preview.copy()
        cr_width = pupil_width = -1
        Processor = self.pupil_processor
        if blink == 0:

            self.rplace_markers(frame_preview)
            for index, cr_processor in enumerate(config.engine.cr_processors):
                if cr_processor.active:

                    cr_corners = cr_processor.corners
                    cr_center, cr_width, cr_height, cr_angle, cr_dimensions_int = cr_processor.ellipse.parameters()

                    if self._state == "adjustment":
                        if cr_processor == self.current_cr_processor:
                            color = bluish
                        else:
                            color = green
                        try:

                            cv2.ellipse(frame_preview, tuple_int(cr_center), cr_dimensions_int, cr_angle, 0, 360, color,
                                        1)
                            self.place_cross(frame_preview, cr_center, color)
                            cv2.rectangle(frame_preview, cr_corners[0], cr_corners[1], color)

                            cv2.putText(frame_preview, "{}".format(index + 2),
                                        (int((cr_corners[1][0] + cr_corners[0][0]) * .5 - 3), cr_corners[0][1] - 3),
                                        font, .7, color, 0, cv2.LINE_4)
                        except Exception as e:
                            cr_processor.active = False

                    else:
                        self.place_cross(frame_preview, cr_center, bluish)

            try:

                pupil_corners = Processor.corners
                pupil_center, pupil_width, pupil_height, pupil_angle, pupil_dimensions_int = Processor.ellipse.parameters()

                cv2.ellipse(frame_preview, tuple_int(pupil_center), pupil_dimensions_int, pupil_angle, 0, 360, red, 1)
                self.place_cross(frame_preview, pupil_center, red)
                cv2.rectangle(frame_preview, pupil_corners[0], pupil_corners[1], red)
            except:
                pass

        if self._state == "adjustment":
            stock_P = self.PStock.copy()
            stock_CR = self.CRStock.copy()

            if cr_width != -1:

                cr_area = self.current_cr_processor.area

                offset_y = int((self.binary_height - cr_area.shape[0]) / 2)
                offset_x = int((self.binary_width - cr_area.shape[1]) / 2)
                stock_CR[offset_y:min(offset_y + cr_area.shape[0], self.binary_height),
                offset_x:min(offset_x + cr_area.shape[1], self.binary_width)] = cr_area
                stock_CR[0:20, 0:self.binary_width] = self.crstock_txt_selected
            else:
                stock_CR[0:20, 0:self.binary_width] = self.crstock_txt

            if pupil_width != -1:
                # stock_P[pcorners[0][1]:pcorners[0][1]+Processor.area.shape[0],
                # pcorners[0][0]:pcorners[0][0]+Processor.area.shape[1]] = Processor.area
                stock_P[0:20, 0:self.binary_width] = self.pstock_txt_selected

                pupil_area = Processor.area

                offset_y = int((self.binary_height - pupil_area.shape[0]) / 2)
                offset_x = int((self.binary_width - pupil_area.shape[1]) / 2)
                stock_P[offset_y:min(offset_y + pupil_area.shape[0], self.binary_height),
                offset_x:min(offset_x + pupil_area.shape[1], self.binary_width)] = pupil_area

            else:
                stock_P[0:20, 0:self.binary_width] = self.pstock_txt

            cv2.putText(stock_P, "{} || {}".format(round(Processor.binarythreshold, 1), Processor.blur),
                        (10, self.binary_height - 10), font, .7, 255, 0, cv2.LINE_4)
            cv2.putText(stock_CR, "{} || {}".format(round(self.current_cr_processor.binarythreshold, 1),
                                                    self.current_cr_processor.blur), (10, self.binary_height - 10),
                        font, .7, 255, 0, cv2.LINE_4)

            frame_source[0:20, 0:self.width] = self.src_txt
            frame_preview[0:20, 0:self.width] = self.prev_txt
            frame_preview[0:self.height, 0:1] = 0

            cv2.putText(frame_source, "#" + str(config.importer.frame), (to_int(self.width / 2), 12), font, .7,
                        (255, 255, 255), 0, cv2.LINE_4)
            i = 0
            while i < 5:
                frame_source[to_int(self.height * i / 5) - 1:to_int(self.height * i / 5) + 1, 0:self.width] = (
                    100, 100, 100)
                i += 1

            #cv2.imshow("CONFIGURATION", np.hstack((frame_source, frame_preview)))
            self.send_frame_with_context(np.hstack((frame_source, frame_preview)), 0)
            #cv2.imshow("BINARY", np.vstack((stock_P, stock_CR)))
            self.send_frame_with_context(np.vstack((stock_P, stock_CR)), 1)

            self.out.write(frame_preview)
            
            try:
                self.gui_data = self.client_socket.recv(20)
                meta = self.gui_data[:self.gui_data_payload_size]
                self.gui_data = self.gui_data[self.gui_data_payload_size:]
                remote_key, x, y = struct.unpack(">iii", meta)
                self.cursor = (x % self.width, y)
                print(int(remote_key), x, y)
                self.key_listener(remote_key)
            except socket.timeout:
                #print('timeout')
                pass
            if not self.gui_data:
                #print('empty')
                pass
            #self.key = cv2.waitKey(50)

            #if self.key == ord("-"):
            #    cv2.imwrite("screen_cap_fr{}.jpg".format(config.importer.frame), frame_preview)

            #self.key_listener(self.key)

        else:
            # real tracking
            self.out.write(frame_preview)

            #cv2.imshow("TRACKING", frame_preview)
            self.send_frame_with_context(frame_preview, 2)

            key = cv2.waitKey(1)

            if key == ord("q"):
                config.engine.release()
