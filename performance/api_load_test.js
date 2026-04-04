import http from "k6/http";
import { check, sleep, group } from "k6";

const BASE_URL = "https://jsonplaceholder.typicode.com";

export const options = {
  stages: [
    { duration: "10s", target: 5 },
    { duration: "20s", target: 10 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    "http_req_duration{name:get_post}": ["p(95)<400"],
    "http_req_duration{name:create_post}": ["p(95)<600"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  // mirrors: test_get_post_returns_200 + test_post_schema_is_correct
  group("GET single post", () => {
    const res = http.get(`${BASE_URL}/posts/1`, { tags: { name: "get_post" } });
    check(res, {
      "status is 200": (r) => r.status === 200,
      "has id field": (r) => JSON.parse(r.body).id === 1,
      "has title field": (r) => JSON.parse(r.body).title !== undefined,
      "response under 400ms": (r) => r.timings.duration < 400,
    });
  });

  // mirrors: test_create_post_returns_201
  group("POST create post", () => {
    const payload = JSON.stringify({
      title: "k6 load test",
      body: "performance test content",
      userId: 1,
    });
    const res = http.post(`${BASE_URL}/posts`, payload, {
      headers: { "Content-Type": "application/json" },
      tags: { name: "create_post" },
    });
    check(res, {
      "status is 201": (r) => r.status === 201,
      "title matches": (r) => JSON.parse(r.body).title === "k6 load test",
    });
  });

  sleep(1);
}
