import schedule,BAutoLike,time
from BAutoLike import SimpleDynamicLiker

liker = SimpleDynamicLiker("310d7da3%2C1618851581%2C03df4*a1") # type:SimpleDynamicLiker
liker.addFilter(BAutoLike.isOfficialClan)

schedule.every(1).minutes.do(liker.likeNew)

while True:
    schedule.run_pending()
    time.sleep(30)