from cache import BaseCache, CacheRequest

class Node:
    def __init__(self, key):
        self.key = key
        self.prev = None
        self.next = None

class ARCCache(BaseCache):
    def __init__(self, size: int, block_size: int, filename: str):
        super().__init__(size, block_size, filename)
        self.name = "ARCCache"
        self.p = 0  # Adaptive parameter balancing LRU and LFU
        self.t1_head = None  # LRU list head
        self.t1_tail = None  # LRU list tail
        self.t2_head = None  # LFU list head
        self.t2_tail = None  # LFU list tail
        self.b1_head = None  # LRU ghost list head
        self.b1_tail = None  # LRU ghost list tail
        self.b2_head = None  # LFU ghost list head
        self.b2_tail = None  # LFU ghost list tail
        self.t1_len = 0  # Length of LRU list
        self.t2_len = 0  # Length of LFU list
        self.b1_len = 0  # Length of LRU ghost list
        self.b2_len = 0  # Length of LFU ghost list
        self.b1 = {}  # Dictionary for b1 cache
        self.b2 = {}  # Dictionary for b2 cache
        self.t1 = {}  # Dictionary for t1 cache
        self.t2 = {}  # Dictionary for t2 cache

    def _remove_node(self, node, list_name):
        # Update the previous and next pointers
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev

        # Update the head and tail pointers
        if node == getattr(self, f"{list_name}_head"):
            setattr(self, f"{list_name}_head", node.next)
        if node == getattr(self, f"{list_name}_tail"):
            setattr(self, f"{list_name}_tail", node.prev)

        # Decrease the length of the list
        setattr(self, f"{list_name}_len", getattr(self, f"{list_name}_len") - 1)

    def _add_node(self, key, list_name):
        node = Node(key)
        current_head = getattr(self, f"{list_name}_head")
        if current_head:
            current_head.prev = node
            node.next = current_head
        setattr(self, f"{list_name}_head", node)
        if getattr(self, f"{list_name}_tail") is None:
            setattr(self, f"{list_name}_tail", node)
        setattr(self, f"{list_name}_len", getattr(self, f"{list_name}_len") + 1)
        getattr(self, list_name)[key] = node

    def _move_to_end(self, node, list_name):
        current_tail = getattr(self, f"{list_name}_tail")
        if node == current_tail:
            # Node is already at the end, no action needed
            return

        self._remove_node(node, list_name)

        # If the tail is None (empty list), set both head and tail to this node
        if current_tail is None:
            setattr(self, f"{list_name}_head", node)
            setattr(self, f"{list_name}_tail", node)
        else:
            # Link the current tail to this node and update the tail pointer
            current_tail.next = node
            node.prev = current_tail
            setattr(self, f"{list_name}_tail", node)
        
        node.next = None


    # def _remove_node(self, node):
    #     if node and node.prev:
    #         node.prev.next = node.next
    #     else:
    #         self.t1_head = node.next if node else None
    #     if node and node.next:
    #         node.next.prev = node.prev
    #     else:
    #         if node and node.prev:
    #             node.prev.next = node.next
    #         else:
    #             self.t1_head = node.next if node else None

    def replace(self, tag):
        if self.t1_len > 0 and (tag in self.b2 or self.t1_len > self.p):
            old_node = self.t1_head
            self.t1_head = old_node.next
            if self.t1_head:
                self.t1_head.prev = None
            else:
                self.t1_tail = None
            self.b1[old_node.key] = old_node
            self.b1_len += 1
            self.t1_len -= 1
        else:
            old_node = self.t2_head
            self.t2_head = old_node.next
            if self.t2_head:
                self.t2_head.prev = None
            else:
                self.t2_tail = None
            self.b2[old_node.key] = old_node
            self.b2_len += 1
            self.t2_len -= 1

    def access(self, cache_request: CacheRequest) -> None:
        self.accesses += 1
        tag = cache_request.tag

        # Case 1: Hit in t1 or t2
        if tag in self.t1:
            self.hits += 1
            node = self.t1[tag]
            self._move_to_end(node, "t1")
            self.t2[tag] = node
            del self.t1[tag]
        elif tag in self.t2:
            self.hits += 1
            node = self.t2[tag]
            self._move_to_end(node, "t2")

        # Case 2: Miss but in b1 or b2
        elif tag in self.b1:
            self.misses += 1
            self.p = min(self.p + max(self.b2_len / self.b1_len, 1), self.num_blocks)
            node = self.b1[tag]
            self.replace(tag)
            self._remove_node(node, "b1")
            if self.t1_tail:
                self.t1_tail.next = node
            else:
                self.t1_head = node
            node.prev = self.t1_tail
            node.next = None
            self.t1_tail = node
            del self.b1[tag]
        elif tag in self.b2:
            self.misses += 1
            self.p = max(self.p - max(self.b1_len / self.b2_len, 1), 0)
            node = self.b2[tag]
            self.replace(tag)
            self._remove_node(node, "b2")
            self.t2[tag] = node
            del self.b2[tag]

        # Case 3: Complete miss
        else:
            self.misses += 1
            if self.t1_len + self.b1_len == self.num_blocks:
                if self.t1_len < self.num_blocks:
                    self._remove_node(self.b1_head, "b1")
                    self.replace(tag)
                else:
                    self.evict()
            elif self.t1_len + self.b1_len < self.num_blocks and self.t1_len + self.t2_len + self.b1_len + self.b2_len >= self.num_blocks:
                if self.t1_len + self.t2_len + self.b1_len + self.b2_len == 2 * self.num_blocks:
                    self._remove_node(self.b2_head, "b2")
                self.replace(tag)
            self._add_node(tag, "t1")

    def evict(self) -> None:
        self.evicts += 1
        self._remove_node(self.t1_head, "t1")
        if self.t1_head:
            self.t1_head = self.t1_head.next
            if self.t1_head:
                self.t1_head.prev = None
            else:
                self.t1_tail = None

    # def _add_node(self, key, head, tail):
    #     node = Node(key)
    #     if head:
    #         node.next = head
    #         head.prev = node
    #     else:
    #         tail = node
    #     head = node
    #     self.t1[key] = node
    #     self.t1_len += 1

    # def _move_to_end(self, node, head, tail):
    #     def _remove_node(self, node):
    #         if node.next:
    #             node.next.prev = node.prev
    #         else:
    #             if node.prev:
    #                 node.prev.next = None
    #             else:
    #                 self.t1_head = None
    #         if node.prev:
    #             node.prev.next = node.next
    #         else:
    #             self.t1_head = node.next
    #         node.prev = None
    #         node.next = None

    #     if tail:
    #         tail.next = node
    #     else:
    #         head = node
    #     tail = node
    #     return head, tail
