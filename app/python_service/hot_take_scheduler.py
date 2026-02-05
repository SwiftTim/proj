from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from hot_take_extractor import HotTakeExtractor
import asyncio
from datetime import datetime
import pytz

class HotTakeScheduler:
    """
    Background scheduler for daily hot take extraction.
    
    Runs once per day at 2:00 AM EAT (East Africa Time) to extract
    trending fiscal topics using Gemini 2.5 Flash.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.extractor = HotTakeExtractor()
        self.timezone = pytz.timezone('Africa/Nairobi')  # EAT timezone
    
    async def daily_extraction_job(self):
        """
        The scheduled job that runs daily.
        """
        print(f"\n{'='*60}")
        print(f"🔥 DAILY HOT TAKE EXTRACTION - {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"{'='*60}\n")
        
        try:
            result = await self.extractor.run_daily_extraction()
            
            if result["status"] == "success":
                print(f"✅ Daily extraction completed successfully")
                print(f"📊 Hot Takes: {len(result['data'].get('hot_takes', []))}")
            else:
                print(f"❌ Daily extraction failed: {result['message']}")
                
        except Exception as e:
            print(f"❌ Scheduler job error: {str(e)}")
        
        print(f"\n{'='*60}\n")
    
    def start(self):
        """
        Starts the scheduler with daily job at 6:00 AM EAT.
        """
        # Schedule daily extraction at 6:00 AM EAT
        self.scheduler.add_job(
            self.daily_extraction_job,
            trigger=CronTrigger(hour=6, minute=0, timezone=self.timezone),
            id='daily_hot_take_extraction',
            name='Daily Hot Take Extraction',
            replace_existing=True
        )
        
        # Optional: Run immediately on startup for testing (comment out in production)
        # self.scheduler.add_job(
        #     self.daily_extraction_job,
        #     trigger='date',
        #     id='startup_hot_take_extraction',
        #     name='Startup Hot Take Extraction'
        # )
        
        self.scheduler.start()
        print(f"✅ Hot Take Scheduler started")
        print(f"📅 Next run: {self.scheduler.get_job('daily_hot_take_extraction').next_run_time}")
    
    def stop(self):
        """
        Stops the scheduler gracefully.
        """
        self.scheduler.shutdown()
        print("🛑 Hot Take Scheduler stopped")
    
    def trigger_manual_extraction(self):
        """
        Manually trigger extraction (for testing or admin purposes).
        """
        print("🔧 Manual extraction triggered...")
        asyncio.create_task(self.daily_extraction_job())


# Singleton instance
_scheduler_instance = None

def get_scheduler() -> HotTakeScheduler:
    """
    Get or create the global scheduler instance.
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = HotTakeScheduler()
    return _scheduler_instance


# Test function
if __name__ == "__main__":
    import signal
    
    scheduler = HotTakeScheduler()
    scheduler.start()
    
    # Keep the script running
    print("Press Ctrl+C to stop...")
    
    def signal_handler(sig, frame):
        print("\n🛑 Stopping scheduler...")
        scheduler.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep alive
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        scheduler.stop()
