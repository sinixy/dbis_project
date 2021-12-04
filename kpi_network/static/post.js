// /posts/:channelId [GET]
const postGetResponse = {
  data: {
    id: 1,
    text: 'bla bla',
    channelId: 3,
    author: {
      id: 1,
      login: 'масло1337',
      name: 'маслянко',
      status: 'lecturer',
      department: 'ПМА',
      photo: null, // || string
    },
  },

  errors: [],
};

// /posts/ [POST]
const postPostPayload = {
  text: 'bla bla',
  channelId: 3,
};

const postsPostResponse = {
  data: {
    id: 23,
  },
  errors: [],
};
