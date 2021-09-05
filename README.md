# tgvc-video-tests [![Awesome](https://img.shields.io/badge/Contain-BUGS-d445ff?style=for-the-badge&labelColor=4c13a8&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAMAAAAolt3jAAAACXBIWXMAAA6sAAAOrAHcqGKDAAAA8FBMVEVHcEwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACvbPJ9AAAAT3RSTlMA4seCvZFjArUDB00cInTFZpsmJbBlISlxLrwIegx7fw5RCoMJZJIdTq4LJ8TZN8usKDhpJLiFaF9zV6la0FkqxjDKL6q5K7bJWLRHscBJVBjMZwAAAKZJREFUCNctjtcWgkAMRAMIiwKCSrf33nvvveT//8ZdMS8zN8mcMwCgSAOg0ynnmYAalzaX7cJoVimE2YZHPMAfCDi+IJz31AAMYyfPNj/PV9xZxqIwS3gyh/wbuevRlljCRfQfiC7zmnXXEUMy4m5ljCAxt24BrqfRPnsQApz8WkREPkC9UqKYKUIPxybWIZtixxw02t0WV4C0mARCaDVVqWlUCPkCu1AVzl8xaMsAAAAASUVORK5CYII=)](https://awesome.re) <img src="https://forthebadge.com/images/badges/it-works-why.svg" alt="" width="155">
Just for testing video streaming using pytgcalls.

#### **Note**: The features used in this repository is highly experimental and you might not get the result you wanted to see.

This bot works partially and this feature is still in beta and it is still experimental
If you see any other repo like this, **Consider the person who made it as dumb** :)

## Deploy

It's better to locally host it, you can also (ab)use [Github workflows](#ways-for-deployment) 
The run command is `python -m vcbot` btw :)
## Environmental variables

- `API_ID` : Get this value from my.telegram.org/apps
- `API_HASH` : Get this value from my.telegram.org/apps
- `SESSION` : visit [here](https://replit.com/@ayrahikari/pyrogram-session-maker) to obtain this value.
- `SUDO` : User IDs of users who have access to use the bot commands. Separate each with space.
- `BOT_TOKEN` : (Optional) Get this value from [BotFather](https://telegram.dog/BotFather).

## Ways for Deployment

<details>
    <summary>  Run on workflows (easy af)</summary>
    
* Fork this repository.
* Goto your forked repository settings.
* Scroll down and select `secrets` tab.
* Click on `New repository secret` button.
* Add the environmental vars as mentioned here.
* After adding all, Goto the `Actions` tab and start the workflows.
    
</details>  

<details>
    <summary>  Heroku?</summary>

- Click the button to deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy) 
</details>

<details>
    <summary>  Railway?</summary>
    
Asked one of the devs and he told me:
![;-;](https://i2.paste.pics/DR0LO.png)
![;-;](https://i2.paste.pics/DR0M4.png)

**Conclusion** : `Pending..`

Still wanna get banned? here

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2FEverythingSuckz%2Ftgvc-video-tests%2Ftree%2Fbeta&envs=API_ID%2CAPI_HASH%2CSESSION%2CSUDO%2CBOT_TOKEN&optionalEnvs=BOT_TOKEN&API_IDDesc=Get+this+value+from+https%3A%2F%2Fmy.telegram.org%2Fapps&API_HASHDesc=Get+this+value+from+my.telegram.org%2Fapps&SESSIONDesc=get+it+from+https%3A%2F%2Freplit.com%2F%40ayrahikari%2Fpyrogram-session-maker&SUDODesc=The+user+IDs+of+users+who+have+access+to+bot+commands&BOT_TOKENDesc=Get+this+from+%40BotFather&SUDODefault=919209968&referralCode=WRENCH)   
</details>  

## Known Issues

- ~~Video and audio sync issues.~~ (not anymore)
- Some stream links may not be streamed.
- Less audio quality.
- breaks / lags in video when you play live videos
- ~~In workflows, the `!stop` commands usually kills the whole bot.~~

## FaQ

<details>
    <summary>  I encountered an issue.. What will I do?</summary>

* Give up :)

</details>  


Made with [Py-TgCalls](https://github.com/pytgcalls/pytgcalls) and [pyrogram](https://github.com/pyrogram/pyrogram) ❤️