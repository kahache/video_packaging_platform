#!/bin/bash

# Only one function
# python3 -m unittest test_video_ops.test_video_ops.test_video_fragment -v

# We start the database
#python3 -m unittest test_database.py -v

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

            OPTIONS=(1 "OJETEDownload test videos"
                     2 "OJETETest EVERYTHING"
                     3 "OJETETest only Video Operations"
                     4 "OJETETest Database consistency"
                     5 "OJETETest main App's functions")

            CHOICE=$(dialog --clear \
                            --backtitle "$BACKTITLE" \
                            --title "$TITLE" \
                            --menu "$MENU" \
                            $HEIGHT $WIDTH $CHOICE_HEIGHT \
                            "${OPTIONS[@]}" \
                            2>&1 >/dev/tty)
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
                        echo "You chose Option 3 - Test EVERYTHING"
                        python3 -m unittest test_video_ops.py -v
                        ;;
                    4)
                        echo "You chose Option 4"
                        ;;
                    5)
                        echo "You chose Option 5"
                        ;;
            esac
            ;;
        4)
            echo "You chose Option 4 - Test Database consistency"
            ;;
        5)
            echo "You chose Option 5 - Test main App's functions"
            ;;
esac
