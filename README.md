# douglass
Jupyter notebook preview service

### Description
Your web-app needs to display read-only versions of Jupyter notebooks. 

Under the hood, Jupyter .ipynb files are JSON documents with a particular [format](https://nbformat.readthedocs.io). Jupyter provides a commandline tool / library [nbconvert](https://nbconvert.readthedocs.io) for interacting with these documents and converting them to various formats, in particular HTML.

This project is essentially nbconvert as a REST service. It takes notebook JSON and returns HTML that can be embedded in your application.

There are two routes:

/status is a health-check endpoint. It accepts GET requests and returns 200 'OK'.

/api/convert is the primary conversion endpoint. It accepts POST requests containing notebook JSON and returns HTML for displaying the notebook's content in the browser.
(Note: I would prefer to include a version in the convert endpoint. Calhoun does not, so I am keeping the endpoint un-versioned for the sake of similarity.)

### Framework.
This project uses the [Sanic](https://sanic.readthedocs.io) Python web framework. Calhoun was written in Node.js and made use Node's async/await syntax. A couple of factors argue in favor of asynchronous request handling being an important feature:
1. The conversion itself may take some time
2. The intended authorization method involves a call to another webservice, which may take variable time
3. The intended consumer is a web-app with hundreds-to-thousands of monthly engaged users, and notebook previewing is a relatively common user task.

Python 3.5 introduced concurrency through coroutines supported by async/await syntax. Several web frameworks make use of asyncio. I narrowed my search to aiohttp and Sanic. Some online reading provided anecdotal evidence indicated that performance was good for both frameworks. I appreciated Sanic's simple syntax, and thought it would be convenient for a small project like this, and readable for programmers coming from Node.

### Background
This project is primarily intended to provide preview versions of notebooks for the [Terra](https://www.terra.bio) research environment. It is based on [Calhoun](https://github.com/DataBiosphere/calhoun), a similar service written in Node.js. The service is written wholly in Python 3.7, so that it can be deployed in the Google App Engine Standard environment. Calhoun used Node and shelled out to nbconvert. Since it required both Node and Python, it needed GAE Flexible which lacks FedRAMP certification.

There is an argument to be made that the client application should interpret notebook JSON and handle it's own styling. It seems like it would be faster, and would eliminate the additional infrastructure. It could also be more customizable to the app context. But this app is fairly simple, and there's precedent that it works well for it's intended purpose. 

As an additional primary aim, this served as a well-defined personal project. Small, well-scoped, and isolated. A great opportunity to write a simple API server entirely in Python.

