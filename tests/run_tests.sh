#!/bin/bash
#__author__ = "Ka Hache a.k.a. The One & Only Javi"
#__version__ = "1.0.0"
#__start_date__ = "06/08/2020"
#__end_date__ = "06/08/2020"
#__maintainer__ = "me"
#__email__ = "little_kh@hotmail.com.com"
#__status__ = "In production"
#__description__ = "Main unit test & integration test script"

# Main Menu
HEIGHT=15
WIDTH=40
CHOICE_HEIGHT=4
BACKTITLE="Video Packaging Platform Tests"
TITLE="Welcome! Select specific test to run"
MENU="Choose one of the following options:"

OPTIONS=(1 "Download test videos"
         2 "Test EVERYTHING"
         3 "Test only Video Operations"
         4 "Test Database consistency"
         5 "Test main App's functions")

CHOICE=$(dialog --clear \
                --backtitle "$BACKTITLE" \
                --title "$TITLE" \
                --menu "$MENU" \
                $HEIGHT $WIDTH $CHOICE_HEIGHT \
                "${OPTIONS[@]}" \
                2>&1 >/dev/tty)

clear
case $CHOICE in
        1)
            echo "You chose Option 1 - Download test videos"
            cd TEST_VIDEOS
            bash download_videos.sh
            ;;
        2)
            echo "You chose Option 2 - Test EVERYTHING"
            python3 -m unittest test_video_ops.py -v
            python3 -m unittest test_database.py -v
            python3 -m unittest test_models.py -v
            python3 -m unittest test_app.py -v
            ;;
        3)
            #echo "You chose Option 3 - Test Video Operations"
            HEIGHT=15
            WIDTH=40
            CHOICE_HEIGHT=4
            BACKTITLE="Video Packaging Platform Tests"
            TITLE="Video Operations menu"
            MENU="Choose one of the following options:"

            OPTIONS=(1 "Test ALL Video Operations"
                     2 "Test video ingestion"
                     3 "Test video fragmentation"
                     4 "Test video encryption"
                     5 "Test MPEG-DASH transcoding")

            CHOICE=$(dialog --clear \
                            --backtitle "$BACKTITLE" \
                            --title "$TITLE" \
                            --menu "$MENU" \
                            $HEIGHT $WIDTH $CHOICE_HEIGHT \
                            "${OPTIONS[@]}" \
                            2>&1 >/dev/tty)
            case $CHOICE in
                    1)
                        echo "You chose Option 1 - Test ALL Video Operations"
                        python3 -m unittest test_video_ops.py -v
                        ;;
                    2)
                        echo "You chose Option 2 - Test video ingestion"
                        python3 -m unittest test_video_ops.test_video_ops.test_video_ingest -v
                        ;;
                    3)
                        echo "You chose Option 3 - Test video fragmentation"
                        python3 -m unittest test_video_ops.test_video_ops.test_video_fragment -v
                        ;;
                    4)
                        echo "You chose Option 4 - Test video encryption"
                        python3 -m unittest test_video_ops.test_video_ops.test_video_encrypt -v
                        ;;
                    5)
                        echo "You chose Option 5 - Test MPEG-DASH transcoding"
                        python3 -m unittest test_video_ops.test_video_ops.test_video_dash -v
                        ;;
            esac
            ;;
        4)
            #echo "You chose Option 4 - Test Database consistency"
            HEIGHT=15
            WIDTH=40
            CHOICE_HEIGHT=4
            BACKTITLE="Video Packaging Platform Tests"
            TITLE="Database consistency menu"
            MENU="Choose one of the following options:"

            OPTIONS=(1 "Test ALL Database consistency"
                     2 "Test Database declaration"
                     3 "Test database model")

            CHOICE=$(dialog --clear \
                            --backtitle "$BACKTITLE" \
                            --title "$TITLE" \
                            --menu "$MENU" \
                            $HEIGHT $WIDTH $CHOICE_HEIGHT \
                            "${OPTIONS[@]}" \
                            2>&1 >/dev/tty)
            case $CHOICE in
                    1)
                        echo "Test ALL Database consistency"
                        python3 -m unittest test_database.py -v
                        python3 -m unittest test_models.py -v
                        ;;
                    2)
                        echo "Test Database declaration"
                        python3 -m unittest test_database.py -v
                        ;;
                    3)
                        echo "Test database model"
                        python3 -m unittest test_models.py -v
                        ;;
            esac
            ;;
        5)
            #echo "You chose Option 5 - Test main App's functions"
            HEIGHT=15
            WIDTH=80
            CHOICE_HEIGHT=4
            BACKTITLE="Video Packaging Platform Tests"
            TITLE="Test main App's functions"
            MENU="Choose one of the following options:"

            OPTIONS=(1 "Test ALL main App's functions"
                     2 "Test when a file is received"
                     3 "Test when a packaging job is called"
                     4 "Test when the status of the packaging job is consulted"
                     5 "Test if the main API how-to is up")

            CHOICE=$(dialog --clear \
                            --backtitle "$BACKTITLE" \
                            --title "$TITLE" \
                            --menu "$MENU" \
                            $HEIGHT $WIDTH $CHOICE_HEIGHT \
                            "${OPTIONS[@]}" \
                            2>&1 >/dev/tty)
            case $CHOICE in
                    1)
                        echo "Test ALL main App's functions"
                        python3 -m unittest test_app.py -v
                        ;;
                    2)
                        echo "Test when a file is received"
                        python3 -m unittest test_app.test_functions.test_success -v
                        ;;
                    3)
                        echo "Test when a packaging job is called"
                        python3 -m unittest test_app.test_functions.test_package -v
                        ;;
                    4)
                        echo "Test when the status of the packaging job is consulted"
                        python3 -m unittest test_app.test_functions.test_consult_status -v
                        ;;
                    5)
                        echo "Test database model"
                        python3 -m unittest test_app.test_functions.test_index -v
                        ;;
            esac
            ;;
esac
