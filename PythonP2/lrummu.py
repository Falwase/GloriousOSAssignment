from mmu import MMU


class LruMMU(MMU):
    def __init__(self, frames):
        self.frameList = [-1] * frames
        self.isModified = [-1] * frames
        self.timeAdded = [-1] * frames
        self.readCount = 0
        self.writeCount = 0
        self.faultCount = 0
        self.clock = 0

    def set_debug(self):
        # TODO: Implement the method to set debug mode
        pass

    def reset_debug(self):
        # TODO: Implement the method to reset debug mode
        pass

    def read_memory(self, page_number):

        if (page_number in self.frameList):
            index = self.frameList.index(page_number)
            self.timeAdded[index] = self.clock
            self.clock += 1
            return

        self.faultCount += 1
        self.readCount += 1

        if(-1 in self.frameList):
            index = self.frameList.index(-1)
        else:
            minTime = min(self.timeAdded)
            index = self.timeAdded.index(minTime)
            
        if(self.isModified[index] == 1):
           self.writeCount  += 1

        self.frameList[index] = page_number
        self.isModified[index] = 0
        self.timeAdded[index] = self.clock

        self.clock += 1

    def write_memory(self, page_number):

        if (page_number in self.frameList):
            index = self.frameList.index(page_number)
            self.isModified[index] = 1
            self.timeAdded[index] = self.clock
            self.clock += 1
            return

        self.faultCount += 1
        self.readCount += 1

        if(-1 in self.frameList):
            index = self.frameList.index(-1)
        else:
            minTime = min(self.timeAdded)
            index = self.timeAdded.index(minTime)
            
        if(self.isModified[index] == 1):
           self.writeCount  += 1

        self.frameList[index] = page_number
        self.isModified[index] = 1
        self.timeAdded[index] = self.clock

        self.clock += 1

    def get_total_disk_reads(self):
        return self.readCount

    def get_total_disk_writes(self):
        return self.writeCount

    def get_total_page_faults(self):
        return self.faultCount
