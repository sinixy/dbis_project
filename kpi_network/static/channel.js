// /channel/:id [GET]
const userGetResponse = {
  data: {
    id: 1,
    name: 'work',
    creatorId: 33,
    photo: null, // || string
  },
  errors: [],
};

// /channel/:id [POST]
const channelPostPayload = {
  name: 'study',
  photo: null, // || string
  members: [2, 4, 5, 6], // array of members' ids (TO BE DONE)
};

const channelPostResponse = {
  data: {
    id: 23,
  },
  errors: [],
};

// /channel/:id [PUT]
const channelPutPayload = {
  name: 'study',
  photo: null, // || string
  members: [2, 4, 5, 6], // array of members' ids (TO BE DONE)
};

const userPutResponse = {
  data: {},
  errors: [],
};

// /channel/:id/members?part=3&limit=2 [GET] (TO BE DONE)
const channelMemebersGetResponse = {
  data: {
    items: [
      {
        id: 1,
        login: 'масло1337',
        name: 'маслянко',
        status: 'lecturer',
        department: 'ПМА',
        photo: null, // || string
      },
      {
        id: 2,
        login: 'shiyak1337',
        name: 'bogdan',
        status: 'student',
        group: 'FR-45',
        photo: null, // || string
      },
    ],

    total: 20,
  },
  errors: [],
};

// /channel/:id/posts?part=3&limit=2 [GET] (TO BE DONE)
const channelPostsGetResponse = {
  data: {
    items: [
      {
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
      {
        id: 2,
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
    ],

    total: 20,
  },
  errors: [],
};
