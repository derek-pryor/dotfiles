import XMonad
import XMonad.Hooks.DynamicLog
import XMonad.Hooks.ManageDocks
import XMonad.Util.Run(spawnPipe)
import XMonad.Util.EZConfig(additionalKeys)
import System.IO

main = do
    xmproc <- spawnPipe "xmobar"
    xmonad $ docks def
        { manageHook = manageDocks <+> manageHook def
        , layoutHook = avoidStruts $ layoutHook def
        , logHook = dynamicLogWithPP xmobarPP
                        { ppOutput = hPutStrLn xmproc
                        , ppTitle = xmobarColor "green" "" . shorten 50
                        }
        , terminal = "/usr/bin/st -f 'Hack:size=12'"
        , modMask = modMask
        } `additionalKeys`
        [ ((modMask, xK_slash), spawn "xsecurelock")

         -- Media Keys
         ,((0, 0x1008ff94), spawn "bluetooth-toggle") -- XF86Bluetooth doesn't have a named var

         -- Keys to get an OTP code
         ,((modMask .|. shiftMask, xK_o), spawn "pass-osd otp -c 2fa/redhat.com")
         ,((modMask, xK_o), spawn "pass-osd otp 2fa/redhat.com")
        ]
    where
        modMask = mod1Mask -- Left Alt (Win Key is mod4Mask)
