# Token
from Token import botToken, botUsername

# Public libraries
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
import numberize
from threading import Thread
import sys
from datetime import datetime
import time

# Own libraries
import DBH
from NewPrint import Print, EnableLogging, DisableLogging, PrintMainInfo
from SkipUpdates import EnableUpdates, DisableUpdates, IsUpdate
from GetExchangeRates import SheduleUpdate, SheduleCryptoUpdate 
from BlackList import IsUserInBlackList, LoadBlackList
import Processing
from Processing import AnswerText, LoadCurrencies, LoadCrypto, LoadDictionaries, LoadFlags, SearchValuesAndCurrencies, SpecialSplit, TextToDigit
import TextHelper as CustomMarkup
from TextHelper import LoadTexts, GetText
import ListsCache

# Main variables
bot = Bot(token=botToken)
dp = Dispatcher(bot)
IsStartedCount = False

# Public commands
@dp.message_handler(commands=['about'])  # analog about and source
async def AboutMes(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    IsChatExist(message.chat.id, message.chat.type)
    await message.reply(GetText(message.chat.id, "about", message.chat.type), reply_markup = CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))

@dp.message_handler(commands=['help'])
async def HelpMes(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    IsChatExist(message.chat.id, message.chat.type)
    await message.reply(GetText(message.chat.id, "help", message.chat.type), reply_markup = CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))

def CanUserEditSettings(chatID: str, chatType: str, memberStatus: str, AllMembersAreAdministrators: bool = False) -> bool:
    CanUserEditSettings = False
    AllChatSettings = DBH.GetAllSettings(chatID, chatType)
    if chatType == "private":
        CanUserEditSettings = True
    else:
        whoCanEditSettings = AllChatSettings['editSettings']
        if whoCanEditSettings == "everybody":
            CanUserEditSettings = True
        elif chatType == "group":
            
            if AllMembersAreAdministrators == True and whoCanEditSettings == 'admins':
                CanUserEditSettings = True
            elif AllMembersAreAdministrators == True and whoCanEditSettings == 'creator':
                if memberStatus == 'creator':
                    CanUserEditSettings = True
            elif AllMembersAreAdministrators == False:
                if whoCanEditSettings == 'admins' and (memberStatus == "administrator" or memberStatus == "creator") or whoCanEditSettings == 'creator' and memberStatus == "creator":
                    CanUserEditSettings = True
        elif chatType == "supergroup":
            if whoCanEditSettings == 'admins' and (memberStatus == "administrator" or memberStatus == "creator") or whoCanEditSettings == 'creator' and memberStatus == "creator":
                CanUserEditSettings = True
    return CanUserEditSettings

@dp.message_handler(commands=['settings'])
async def SettingsMes(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    IsChatExist(message.chat.id, message.chat.type)
    
    member = await message.chat.get_member(message.from_user.id)
    if CanUserEditSettings(message.chat.id, message.chat.type, member.status, message.chat.all_members_are_administrators):
        await message.reply(GetText(message.chat.id, "main_settings_menu", message.chat.type), reply_markup = CustomMarkup.SettingsMarkup(message.chat.id, message.chat.type))
    else:
        await message.reply(GetText(message.chat.id, "error_main_settings_menu", message.chat.type), reply_markup = CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))


@dp.message_handler(commands=['donate'])
async def DonateMes(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    IsChatExist(message.chat.id, message.chat.type)
    await message.reply(GetText(message.chat.id, "donate", message.chat.type), reply_markup = CustomMarkup.DonateMarkup(message.chat.id, message.chat.type))


@dp.message_handler(commands=['wrong'])
async def WrongMes(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    IsChatExist(message.chat.id, message.chat.type)
    MessageText = message.reply_to_message.text
    if message.photo or message.video is not None or message.document is not None:
        MessageText = message.reply_to_message.caption
    DBH.AddReport(message.chat.id, message.from_user.id, MessageText)

# Admin`s commands
@dp.message_handler(commands=['echo'])
async def EchoVoid(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        MessageToUsers = (message.text).replace("/echo ", "")
        adminList = DBH.GetAdmins()
        for i in adminList:
            await bot.send_message(i, "Начата рассылка сообщения всем пользователям. Текст сообщения:\n\n" + MessageToUsers, reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
        listGC = DBH.GetGroupChatIDs()
        for i in listGC:
            try:
                await bot.send_message(i, MessageToUsers, reply_markup = CustomMarkup.DonateMarkup(i, "private"))
            except:
                Print("Chat " + str(i) + " is not available.", "W")
            time.sleep(0.035)
        listPC = DBH.GetPrivateChatIDs()
        for i in listPC:
            try:
                await bot.send_message(i, MessageToUsers, reply_markup = CustomMarkup.DonateMarkup(i, "private"))
            except:
                Print("Chat " + str(i) + " is not available.", "W")
            time.sleep(0.035)
        for i in adminList:
            await bot.send_message(i, "Рассылка закончена.", reply_markup = CustomMarkup.DeleteMarkup(i, "private"))

@dp.message_handler(commands=['count'])  # Analog of "count".
async def CountVoid(message: types.Message):
    global IsStartedCount
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        if not IsStartedCount:
            isShortVariant = False
            Variant = (message.text).replace("/count", "").replace(" ", "")
            if Variant == "short":
                isShortVariant = True
            adminList = DBH.GetAdmins()
            for i in adminList:
                if not isShortVariant:
                    await bot.send_message(i, "Начат подсчёт количества участников всех чатов.", reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
                else:
                    await bot.send_message(i, "Начат подсчёт количества участников групповых чатов.", reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
            IsStartedCount = True
            CountUsers = 0
            listGC = DBH.GetGroupChatIDs()
            for i in listGC:
                try:
                    CountUsers += await bot.get_chat_members_count(i)
                except:
                    Print("Chat " + str(i) + " not found.", "W")
                time.sleep(0.035)
            if not isShortVariant:
                listPC = DBH.GetPrivateChatIDs()
                for i in listPC:
                    try:
                        CountUsers += await bot.get_chat_members_count(i) - 1
                    except:
                        Print("Chat " + str(i) + " not found.", "W")
                    time.sleep(0.035)
                IsStartedCount = False
            for i in adminList:
                if not isShortVariant:
                    await bot.send_message(i, "Количество участников всех чатов: " + str(CountUsers), reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
                else:
                    await bot.send_message(i, "Количество участников групповых чатов: " + str(CountUsers), reply_markup = CustomMarkup.DeleteMarkup(i, "private"))
        else:
            await message.reply("Подсчёт уже начат.", reply_markup = CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))

@dp.message_handler(commands=['newadmin']) 
async def AddAdminVoid(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        newAdminID = message.text
        newAdminID = newAdminID.replace("/newadmin ", "")
        if newAdminID.isdigit():
            if not DBH.IsAdmin(newAdminID):
                DBH.AddAdmin(newAdminID)
                ListOfAdmins = DBH.GetAdmins()
                if newAdminID in ListOfAdmins:
                    await message.reply("Новый администратор успешно добавлен.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))
                else:
                    await message.reply("Не удалось добавить нового администратора.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))
            else:
                await message.reply("Данный ID уже есть в списке администраторов.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))
        else:
            await message.reply("В ID должны быть только цифры и возможно минус.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))

@dp.message_handler(commands=['stats'])
async def StatsVoid(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        chatStats = DBH.GetChatsAmount()
        answerMes = "ЛС: " + str(chatStats['private']) + "\nГруппы: " + str(chatStats['groups'])
        await message.reply(answerMes, reply_markup=CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))

@dp.message_handler(commands=['fullstats'])
async def FullStatsVoid(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        chatStats = DBH.GetTimeStats()
        answerMes = "За всё время:\nЛС: " + str(chatStats['private']) + "\nГруппы: " + str(chatStats['groups']) + "\n\nЗа неделю:\nЛС: " + str(chatStats['activePrivateWeek']) + "\nГруппы: " + str(chatStats['activeGroupsWeek']) + "\n\nЗа 30 дней:\nЛС: " + str(chatStats['activePrivateMonth']) + "\nГруппы: " + str(chatStats['activeGroupsMonth'])
        await message.reply(answerMes, reply_markup = CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))

@dp.message_handler(commands=['backup']) # analog "backup", "logs" and "reports".
async def BackupVoid(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        nameOfBackup = DBH.CreateAllBackups()
        backupFile = open(nameOfBackup, 'rb')
        await bot.send_document(message.chat.id, backupFile)

@dp.message_handler(commands=['unban'])
async def UnbanVoid(message: types.Message):
    if IsUserInBlackList(message.from_user.id):
        return
    if DBH.IsAdmin(message.from_user.id):
        unbanID = message.text
        unbanID = unbanID.replace("/unban ", "")
        if unbanID.isdigit():
            if DBH.IsBlacklisted(unbanID):
                DBH.ClearBlacklist(unbanID)
                if not DBH.IsBlacklisted(unbanID):
                    await message.reply("Пользователь успешно разблокирован.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))
                else:
                    await message.reply("Не удалось разблокировать пользователя.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))
            else:
                await message.reply("Данный пользователь не находится в ЧС. Разблокировка не возможна.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))
        else:
            await message.reply("В ID должны быть только цифры и минус.", CustomMarkup.GetText(message.chat.id, 'delete', message.chat.type))

# Technical commands
@dp.message_handler(commands=['start'])
async def StartVoid(message: types.Message):
    IsChatExist(message.chat.id, message.chat.type)

@dp.message_handler(content_types=ContentType.ANY)
async def MainVoid(message: types.Message):
    def w2n(MesString: str, lang: str):
        numberizer = numberize.Numberizer(lang=lang)
        return numberizer.replace_numerals(MesString)

    try:
        if message.forward_from.username == botUsername:
            return
    except:
        pass

    # Checking if a user is on the blacklist
    if IsUserInBlackList(message.from_user.id):
        return

    # Get message text
    MessageText = message.text
    if message.photo or message.video is not None or message.document is not None:
        MessageText = message.caption
    if MessageText is None or MessageText == "":
        return

    # Logging basic information to terminal
    PrintMainInfo(message, MessageText)

    # Checking the chat in the database
    IsChatExist(message.chat.id, message.chat.type)

    # word to num
    OriginalMessageText = MessageText
    MessageText = MessageText.lower()
    MessageText = w2n(MessageText, 'uk')
    MessageText = w2n(MessageText, 'ru')
    Print(MessageText, "L")

    # Check digit
    if not any(map(str.isdigit, MessageText)):
        return

    # Preparing a message for searching currencies
    TextArray = SpecialSplit(MessageText)
    Print(str(TextArray), "L")

    # '5kk USD' to '5000000 USD'
    TextArray = TextToDigit(TextArray)
    Print(str(TextArray), "L")
    
    # Searching Currencies
    NumArray = SearchValuesAndCurrencies(TextArray)
    Print(str(NumArray), "L")

    # If there are no currencies, then work is interrupted
    if NumArray == [[],[],[],[]]:
        return

    result = AnswerText(NumArray, message.chat.id, message.chat.type)
    await message.reply(result, parse_mode = "HTML", reply_markup = CustomMarkup.DeleteMarkup(message.chat.id, message.chat.type))
    DBH.UpdateChatUsage(message.chat.id)
    for i in NumArray[1]:
        DBH.ProcessedCurrency(message.chat.id, message.from_user.id, ListsCache.GetListOfCur()[i], OriginalMessageText)
    for i in NumArray[3]:
        DBH.ProcessedCurrency(message.chat.id, message.from_user.id, ListsCache.GetListOfCrypto()[i], OriginalMessageText)

@dp.callback_query_handler(lambda call: True)
async def CallbackAnswer(call: types.CallbackQuery):
    if IsUserInBlackList(call.message.from_user.id):
        return
    if call.data == "delete":
        CanUserDeleteMes = False
        if call.message.chat.type == "private":
            CanUserDeleteMes = True
        else:
            whoCanDeleteMes = DBH.GetSetting(call.message.chat.id, "deleteRules", call.message.chat.type)
            if whoCanDeleteMes == "everybody":
                CanUserDeleteMes = True
            elif call.message.chat.type == "group":
                member = await call.message.chat.get_member(call.from_user.id)
                if call.message.chat.all_members_are_administrators == True and whoCanDeleteMes == 'admins':
                    CanUserDeleteMes = True
                elif call.message.chat.all_members_are_administrators == True and whoCanDeleteMes == 'creator':
                    if member.status == 'creator':
                        CanUserDeleteMes = True
                elif call.message.chat.all_members_are_administrators == False:
                    if whoCanDeleteMes == 'admins' and (member.status == "administrator" or member.status == "creator") or whoCanDeleteMes == 'creator' and member.status == "creator":
                        CanUserDeleteMes = True
            elif call.message.chat.type == "supergroup":
                member = await call.message.chat.get_member(call.from_user.id)
                if whoCanDeleteMes == 'admins' and (member.status == "administrator" or member.status == "creator") or whoCanDeleteMes == 'creator' and member.status == "creator":
                    CanUserDeleteMes = True
        if CanUserDeleteMes:
            try:
                await bot.edit_message_text(call.message.text + "\n\n@" + str(call.from_user.username) + " (id: " + str(call.from_user.id) + ")" + " delete it.", call.message.chat.id, call.message.message_id)
                await call.message.delete()
            except:
                Print("Cannot delete message.", "E")
    elif str(call.data).find("delbut_") == 0:
        member = await call.message.chat.get_member(call.from_user.id)
        if not CanUserEditSettings(call.message.chat.id, call.message.chat.type, member.status, call.message.chat.all_members_are_administrators):
            return
        Index = str(call.data).find("_") + 1
        Value = str(call.data)[Index:len(str(call.data))]
        if Value == "menu":
            pass
        elif Value == "button":
            IsFlag = DBH.GetSetting(call.message.chat.id, 'deleteButton', call.message.chat.type)
            DBH.SetSetting(call.message.chat.id, 'deleteButton', int(not IsFlag), call.message.chat.type)
        else:
            DBH.SetSetting(call.message.chat.id, 'deleteRules', Value, call.message.chat.type)
        await bot.edit_message_text(GetText(call.message.chat.id, 'delete_button_menu', call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.DeleteButtonMenuMarkup(call.message.chat.id, call.message.chat.type))
    
    elif str(call.data).find("lang_") == 0:
        member = await call.message.chat.get_member(call.from_user.id)
        if not CanUserEditSettings(call.message.chat.id, call.message.chat.type, member.status, call.message.chat.all_members_are_administrators):
            return
        Index = str(call.data).find("_") + 1
        Value = str(call.data)[Index:len(str(call.data))]
        if Value == "menu":
            pass
        else:
            DBH.SetSetting(call.message.chat.id, 'lang', Value, call.message.chat.type)
        await bot.edit_message_text(GetText(call.message.chat.id, 'lang_menu', call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.LanguageMenuMarkup(call.message.chat.id, call.message.chat.type))
    
    elif str(call.data).find("flags_") == 0:
        member = await call.message.chat.get_member(call.from_user.id)
        if not CanUserEditSettings(call.message.chat.id, call.message.chat.type, member.status, call.message.chat.all_members_are_administrators):
            return
        Index = str(call.data).find("_") + 1
        Value = str(call.data)[Index:len(str(call.data))]
        if Value == "menu":
            pass
        elif Value == "button":
            IsFlag = DBH.GetSetting(call.message.chat.id, 'flags', call.message.chat.type)
            DBH.SetSetting(call.message.chat.id, 'flags', int(not IsFlag), call.message.chat.type)
        await bot.edit_message_text(GetText(call.message.chat.id, 'flags_menu', call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.FlagsMarkup(call.message.chat.id, call.message.chat.type))

    elif str(call.data).find("edit_") == 0:
        member = await call.message.chat.get_member(call.from_user.id)
        memberStatus = member.status
        if not CanUserEditSettings(call.message.chat.id, call.message.chat.type, memberStatus, call.message.chat.all_members_are_administrators):
            return
        Index = str(call.data).find("_") + 1
        Value = str(call.data)[Index:len(str(call.data))]
        if Value == "menu":
            pass
        else:
            if memberStatus == "member":
                pass
            elif memberStatus == "administrator" and (Value == "admins" or Value == "everybody"):
                DBH.SetSetting(call.message.chat.id, 'editSettings', Value, call.message.chat.type)
            elif memberStatus == "creator":
                DBH.SetSetting(call.message.chat.id, 'editSettings', Value, call.message.chat.type)
        await bot.edit_message_text(GetText(call.message.chat.id, 'edit_menu', call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.EditMenuMarkup(call.message.chat.id, call.message.chat.type))
    
    elif str(call.data).find("cur_") == 0:
        member = await call.message.chat.get_member(call.from_user.id)
        memberStatus = member.status
        if not CanUserEditSettings(call.message.chat.id, call.message.chat.type, memberStatus, call.message.chat.all_members_are_administrators):
            return
        Index = str(call.data).find("_") + 1
        Value = str(call.data)[Index:len(str(call.data))]

        if Value == "menu":
            await bot.edit_message_text(GetText(call.message.chat.id, "currencies_mainmenu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.CurrenciesMainMenuMarkup(call.message.chat.id, call.message.chat.type))
        elif Value == "cryptomenu":
            await bot.edit_message_text(GetText(call.message.chat.id, "crypto_mainmenu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.CryptoMenuMarkup(call.message.chat.id, call.message.chat.type))
        elif Value == "curmenu":
            await bot.edit_message_text(GetText(call.message.chat.id, "currencies_menu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.CurrenciesMenuMarkup(call.message.chat.id, call.message.chat.type))
        elif len(Value) == 1 or len(Value) == 2:
            await bot.edit_message_text(GetText(call.message.chat.id, "letter_menu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.CurrenciesSetupMarkup(call.message.chat.id, call.message.chat.type, Value))
        elif len(Value) == 3 or len(Value) == 4:
            DBH.ReverseCurrencySetting(call.message.chat.id, Value)
            if Value in ListsCache.GetListOfCrypto():
                await bot.edit_message_text(GetText(call.message.chat.id, "crypto_mainmenu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.CryptoMenuMarkup(call.message.chat.id, call.message.chat.type))
            else:
                dictForMU = {'A': 'a', 'B': 'b', 'C': 'c', 'D': 'df', 'E': 'df', 'F': 'df', 'G': 'gh', 'H': 'gh', 'I': 'ij', 'J': 'ij', 'K': 'kl', 'L': 'kl', 'M': 'm', 'N': 'nq', 'O': 'nq', 'P': 'nq', 'Q': 'nq', 'R': 'rs', 'S': 'rs', 'T': 'tu', 'U': 'tu', 'V': 'vy', 'W': 'vy', 'X': 'vy', 'Y': 'vy'}
                await bot.edit_message_text(GetText(call.message.chat.id, "letter_menu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.CurrenciesSetupMarkup(call.message.chat.id, call.message.chat.type, dictForMU[Value[0]]))

    elif call.data == "settings":
        await bot.edit_message_text(GetText(call.message.chat.id, "main_settings_menu", call.message.chat.type), call.message.chat.id, call.message.message_id, reply_markup = CustomMarkup.SettingsMarkup(call.message.chat.id, call.message.chat.type))


def CheckArgument(key: str, value: str) -> bool:
    isAllOkArg = True
    if key == "--logs" or key == "-l":
        if value == "on":
            EnableLogging()
        elif value == "off":
            DisableLogging()
        else:
            isAllOkArg = False
    elif key == "--admin" or key == "-a":
        if value.isdigit():
            if not DBH.IsAdmin(value):
                DBH.AddAdmin(value)
        else:
            isAllOkArg = False
    elif key == "--updates" or key == "-u":
        if value == "on":
            EnableUpdates()
        elif value == "off":
            DisableUpdates()
        else:
            isAllOkArg = False
    else:
        print("Error. Unknow argument '{}'".format(key))
    return isAllOkArg

def IsChatExist(chatID: str, chatType: str):
    if DBH.ChatExists(chatID):
        pass
    else:
        DBH.AddID(chatID, chatType)
        DBH.AddIDStats(chatID, chatType)

def LoadDataForBot():
    DBH.DBIntegrityCheck()
    LoadBlackList()
    LoadCurrencies()
    LoadCrypto()
    LoadFlags()
    LoadDictionaries()
    LoadTexts()

def RegularBackup():
    while True:
        nameOfArch = DBH.CreateAllBackups()
        time.sleep(86400)

def RegularStats():
    while True:
        Stats = DBH.GetSetTimeStats()
        time.sleep(86400)

if __name__ == '__main__':
    LoadDataForBot()

    if len(sys.argv) == 3:
        if not CheckArgument(sys.argv[1], sys.argv[2]):
            sys.exit()
    elif len(sys.argv) == 5 and sys.argv[1] != sys.argv[3]:
        if not CheckArgument(sys.argv[1], sys.argv[2]):
            sys.exit()
        elif not CheckArgument(sys.argv[3], sys.argv[4]):
            sys.exit()
    elif len(sys.argv) == 7 and sys.argv[1] != sys.argv[3] and sys.argv[1] != sys.argv[2] and sys.argv[2] != sys.argv[3]:
        if not CheckArgument(sys.argv[1], sys.argv[2]):
            sys.exit()
        elif not CheckArgument(sys.argv[3], sys.argv[4]):
            sys.exit()
        elif not CheckArgument(sys.argv[5], sys.argv[6]):
            sys.exit()
    elif len(sys.argv) == 5 and not sys.argv[1] != sys.argv[3] or len(sys.argv) == 7 and not (sys.argv[1] != sys.argv[3] and sys.argv[1] != sys.argv[2] and sys.argv[2] != sys.argv[3]):
        Print("Error. Duplicate argument.", "E")
        sys.exit()

    ThreadUpdateExchangeRates = Thread(target = SheduleUpdate)
    ThreadUpdateExchangeRates.start()
    ThreadUpdateCryptoRates = Thread(target = SheduleCryptoUpdate)
    ThreadUpdateCryptoRates.start()
    ThreadRegularBackup = Thread(target = RegularBackup)
    ThreadRegularBackup.start()
    ThreadRegularStats = Thread(target = RegularStats)
    ThreadRegularStats.start()
    executor.start_polling(dp, skip_updates = IsUpdate())