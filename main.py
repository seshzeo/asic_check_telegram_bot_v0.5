from telegram.ext import ApplicationBuilder, CommandHandler, JobQueue, CallbackQueryHandler
from handlers import get_logs, stat, say_hi, change_min_hash, button_handler, check_asic_notification, change_max_temp
import logging, os
from dotenv import load_dotenv
 

logging.basicConfig(
    filename= 'logs.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()


if __name__ == '__main__':
    print(f'Start bot v 0.5')
    job_queue = JobQueue()
    application = (
        ApplicationBuilder()
        .token(os.getenv("API_TOKEN"))
        .job_queue(job_queue)
        .build()
    )
    
    application.add_handlers([
        CommandHandler('stat', stat),
        CommandHandler('hi', say_hi),
        CommandHandler('minhash', change_min_hash),
        CommandHandler('maxtemp', change_max_temp),
        CommandHandler('logs', get_logs),
        CallbackQueryHandler(button_handler),
    ])
    # application.add_error_handler(error_handler)
    job_queue.run_repeating(check_asic_notification, interval=15, first=0)
    
    application.run_polling()